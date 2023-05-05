import boto3
import numpy as np
import hashlib
import ffmpeg
import os
import requests

CACHE_DYNAMODB_TABLE_NAME = os.environ.get('CACHE_DYNAMODB_TABLE_NAME')
ML_API_DNS_NAME = os.environ.get('ML_API_DNS_NAME')
ML_API_BASE_PATH = os.environ.get('ML_API_BASE_PATH', default="/api/v1/")
VID_RES = tuple(os.environ.get('VID_RES', default='240,240').split(','))
VID_DURATION = int(os.environ.get('VID_DURATION', default=2))
TOTAL_OUTPUT_FRAMES = int(os.environ.get('TOTAL_OUTPUT_FRAMES', default=25))

DYNAMODB_CLIENT = boto3.resource('dynamodb')
DYNAMODB_CACHE_TABLE = DYNAMODB_CLIENT.Table(CACHE_DYNAMODB_TABLE_NAME)


process = (
    ffmpeg
    .input('pipe:')
    .video
    .trim(duration=VID_DURATION)
    .filter('framerate', fps=TOTAL_OUTPUT_FRAMES/VID_DURATION)
    .filter('scale', f'{VID_RES[0]}x{VID_RES[1]}')
    .filter('setsar', ratio=f'{VID_RES[0]}/{VID_RES[1]}')
    .output('pipe:', format='rawvideo', pix_fmt='rgb24')
    # .run_async(pipe_stdin=True, pipe_stdout=True)
)


def get_vid_arr_from_bytes(video_bytes: bytes) -> "np.ndarray[np.uint8].shape[TOTAL_OUTPUT_FRAMES, VID_RES[1], VID_RES[0], 3]":
    try:
        vid_raw, _ = process.run(input=video_bytes, capture_stdout=True)
        vid_arr = np.frombuffer(vid_raw, np.uint8).reshape((TOTAL_OUTPUT_FRAMES, VID_RES[1], VID_RES[0], 3))

        return vid_arr
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        raise e

def get_classification(vid_arr: "np.ndarray[np.uint8].shape[TOTAL_OUTPUT_FRAMES, VID_RES[1], VID_RES[0], 3]") -> str:
    vid_arr_hash_hexdigest = hashlib.md5(vid_arr.tobytes()).hexdigest()

    cached_response = DYNAMODB_CACHE_TABLE.get_item(Key={'hash_key': vid_arr_hash_hexdigest})
    if 'Item' in cached_response:
        return cached_response['Item']['class']
    else:
        pred = get_inference(vid_arr)
        DYNAMODB_CACHE_TABLE.put_item(Item={'hash_key': vid_arr_hash_hexdigest, 'class': pred })
        return pred


def get_inference(vid_arr: "np.ndarray[np.uint8].shape[TOTAL_OUTPUT_FRAMES, VID_RES[1], VID_RES[0], 3]") -> str:
    reponse = requests.post(ML_API_DNS_NAME+ML_API_BASE_PATH+'video-classification', data=vid_arr.tobytes())
    return reponse.json()['predicted_class']

