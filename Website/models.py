import boto3
from fastapi import FastAPI
import cv2
import numpy as np
import hashlib
import io 
import subprocess
from moviepy.editor import VideoFileClip
import imghdr
import tempfile
import ffmpeg
import os 






# def process_video(video):
#     video_array = None
#     try:
#         video_buffer = io.BytesIO()
#         video.save(video_buffer)
#         video_array = np.frombuffer(video_buffer.getvalue(), dtype=np.uint8)
#         return video_array
#     except Exception as e:
#         print(str(e))
#         return 'Failed to decode video', 400

def process_video(video_file):
    # Save BytesIO object to temporary file
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(video_file.read())
    tmp.close()

    # Probe the video with ffmpeg
    probe = ffmpeg.probe(tmp.name)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')

    # Get video metadata
    width = int(video_info['width'])
    height = int(video_info['height'])
    fps = int(eval(video_info['avg_frame_rate']))
    num_frames = int(float(video_info['duration']) * fps)

    # Extract frames as numpy array
    out, _ = (
        ffmpeg
        .input(tmp.name)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
        .run(capture_stdout=True)
    )
    video_array = (
        np
        .frombuffer(out, np.uint8)
        .reshape([-1, height, width, 3])
    )

    # Delete temporary file
    os.unlink(tmp.name)

    return video_array

    #return video_array, fps, num_frames, width, height
    # video = io.BytesIO(video_file)
    # clip = VideoFileClip(video)
    # frames = [frame for frame in clip.iter_frames()]
    # frames_array = np.array(frames)
    # return frames_array
    # mp4_file = io.BytesIO(video_file)
    # clip = VideoFileClip(mp4_file)
    # frames = [frame for frame in clip.iter_frames()]
    # frames_array = np.array(frames)
    # clip.reader.close()
    # clip.audio.reader.close_proc()
    # mp4_file.close()
    # frames = []
    # for frame in container.decode(video=0):
    #     frame = np.array(frame.to_image())
    #     frame = cv2.resize(frame, (224, 224))
    #     frames.append(frame)
    # container.close()
    # frames = np.array(frames)
    



    

def validate_db(processed):
    ## hash video 
    ## check database for hash 
    ## return True and result 
    temp = 1

def infer_model(processes):
    temp = 1
    ## callback if not found in database 
    ##  send processes video to lamda using Fast API 
