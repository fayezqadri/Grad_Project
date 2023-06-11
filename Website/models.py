import boto3
import numpy as np
import hashlib
import ffmpeg
import os
import requests
from flask import current_app
import sys
app = current_app

CACHE_DYNAMODB_TABLE_NAME = os.environ.get('CACHE_DYNAMODB_TABLE_NAME')
ML_API_DNS_NAME = os.environ.get('ML_API_DNS_NAME')
ML_API_BASE_PATH = os.environ.get('ML_API_BASE_PATH', default="/api/v1/")
VID_HEIGHT = int(os.environ.get('VID_HEIGHT', default=224))
VID_WIDTH = int(os.environ.get('VID_WIDTH', default=224))
VID_DURATION = int(os.environ.get('VID_DURATION', default=2))
TOTAL_OUTPUT_FRAMES = int(os.environ.get('TOTAL_OUTPUT_FRAMES', default=25))

EC2_AZ = os.environ.get('EC2_AZ')
INSTANCE_ID = os.environ.get('INSTANCE_ID')
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')

boto3.setup_default_session(region_name=AWS_DEFAULT_REGION)
DYNAMODB_CLIENT = boto3.resource('dynamodb')
DYNAMODB_CACHE_TABLE = DYNAMODB_CLIENT.Table(CACHE_DYNAMODB_TABLE_NAME)


process = (
    ffmpeg
    .input('pipe:')
    .video
    .trim(duration=VID_DURATION)
    .filter('fps', fps=TOTAL_OUTPUT_FRAMES/VID_DURATION)
    .filter('scale', f'{VID_WIDTH}x{VID_HEIGHT}')
    .filter('setsar', ratio=f'{VID_WIDTH}/{VID_HEIGHT}')
    .trim(duration=VID_DURATION)
    .output('pipe:', format='rawvideo', pix_fmt='rgb24')
    # .run_async(pipe_stdin=True, pipe_stdout=True)
)


def get_vid_arr_from_bytes(video_bytes: bytes) -> "np.ndarray[np.uint8].shape[TOTAL_OUTPUT_FRAMES, VID_HEIGHT, VID_WIDTH, 3]":
    try:
        vid_raw, _ = process.run(input=video_bytes, capture_stdout=True, capture_stderr=True)
        vid_arr = np.frombuffer(vid_raw, np.uint8).reshape((TOTAL_OUTPUT_FRAMES, VID_HEIGHT, VID_WIDTH, 3))
        vid_arr = vid_arr
        app.logger.info(f"vid_arr size: {sys.getsizeof(vid_arr)/1024**2}")

        return vid_arr
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        app.logger.error(e.stdout.decode('utf8'))

        print('stderr:', e.stderr.decode('utf8'))
        app.logger.error(e.stderr.decode('utf8'))
        raise e

def get_classification(vid_arr: "np.ndarray[np.uint8].shape[TOTAL_OUTPUT_FRAMES, VID_HEIGHT, VID_WIDTH, 3]") -> str:
    vid_arr_hash_hexdigest = hashlib.md5(vid_arr.tobytes()).hexdigest()

    cached_response = DYNAMODB_CACHE_TABLE.get_item(Key={'np-array-hash': vid_arr_hash_hexdigest})
    if 'Item' in cached_response:
        app.logger.info(f'Found in cache table video with arr-hash = {vid_arr_hash_hexdigest}. Returning stored prediction.')

        return cached_response['Item']['class']
    else:
        app.logger.info(f"Couldn't find in cache table video with arr-hash = {vid_arr_hash_hexdigest}. Getting inference from ML model.")

        pred = get_inference(vid_arr)
        if pred is None:
            app.logger.info(f"Got '{pred}' as a prediction from ML model and did not store in cache table.")
            return None

        DYNAMODB_CACHE_TABLE.put_item(Item={'np-array-hash': vid_arr_hash_hexdigest, 'class': pred })
        app.logger.info(f"Got '{pred}' as a prediction from ML model and stored in cache table.")

        return pred


MAX_RETRIES = 3
retries = 0
def get_inference(vid_arr: "np.ndarray[np.uint8].shape[TOTAL_OUTPUT_FRAMES, VID_HEIGHT, VID_WIDTH, 3]") -> str:
    # return 234
    try:
        response = requests.post(ML_API_DNS_NAME+ML_API_BASE_PATH+'video-classification', data=vid_arr.tobytes(), headers={'Content-Type': 'application/octet-stream'})
        app.logger.info(f"Sent the follwoing request to ML API: {response.request}")
        app.logger.info(f"Got the following response from ML API: {response}")
    except Exception as e:
        print(e)
        app.logger.error(e)
        return f'error: {e}'
    try:
        rjson = response.json()
        if 'error' in rjson:
            return rjson
        pred = rjson['predicted_class']

        if pred is None and retries < MAX_RETRIES:
            retries += 1
            get_inference(vid_arr)
        elif pred is None and retries >= MAX_RETRIES:
            return None

        return pred
    except Exception as e:
        app.logger.error(f"{e}")

