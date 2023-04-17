import boto3
from fastapi import FastAPI
import numpy as np
import hashlib
import ffmpeg
import os 



vid_res = (480, 480) # WxH
vid_duration = 2 # seconds
total_output_frames = 25
process = (
            ffmpeg
            .input('pipe:')
            .video
            .trim(duration=vid_duration)
            .filter('framerate', fps=total_output_frames/vid_duration)
            .filter('scale', f'{vid_res[0]}x{vid_res[1]}')
            .filter('setsar', ratio=f'{vid_res[0]}/{vid_res[1]}')
            .output('pipe:', format='rawvideo', pix_fmt='rgb24')
            # .run_async(pipe_stdin=True, pipe_stdout=True)
        )


def process_video(video_bytes):
    try:
        vid_raw, _ = process.run(input=video_bytes, capture_stdout=True)
        vid_arr = np.frombuffer(vid_raw, np.uint8).reshape((-1, vid_res[1], vid_res[0], 3))

        return vid_arr
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        raise e

client = boto3.client('dynamodb')

def get_prediction(processed):

    processed = np.random.rand(24,240,240,3)
    table_name = 'my-table'

    processed_bytes = processed.tobytes()
    hash_video = hashlib.md5(processed_bytes)
    hash_video = hash_video.hexdigest()
    response = client.get_item(
        TableName = table_name,
        Key = {
        "Key_Column_Name":{'S':hash_video}} )
    if 'Item' in response:
        prediction = response['Item']['prediction_column_name']['S']
        return prediction
    else:
        #### Send processed to FAST- API 
        return 1 



    

