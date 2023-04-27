import boto3
import numpy as np
import hashlib
import io
import ffmpeg
import subprocess






# def process_video(video_file):
#     # Save BytesIO object to temporary file
#     tmp = tempfile.NamedTemporaryFile(delete=False)
#     tmp.write(video_file.read())
#     tmp.close()

#     # Probe the video with ffmpeg
#     probe = ffmpeg.probe(tmp.name)
#     video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')

#     # Get video metadata
#     width = int(video_info['width'])
#     height = int(video_info['height'])
#     fps = int(eval(video_info['avg_frame_rate']))
#     num_frames = int(float(video_info['duration']) * fps)

#     # Extract frames as numpy array
#     out, _ = (
#         ffmpeg
#         .input(tmp.name)
#         .output('pipe:', format='rawvideo', pix_fmt='rgb24')
#         .run(capture_stdout=True)
#     )
#     video_array = (
#         np
#         .frombuffer(out, np.uint8)
#         .reshape([-1, height, width, 3])
#     )

#     # Delete temporary file
#     os.unlink(tmp.name)

#     return video_array

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


def process_video(video):
    video_array = None
    try:
        video_buffer = io.BytesIO()
        video.save(video_buffer)
        video_array = np.frombuffer(video_buffer.getvalue(), dtype=np.uint8)
        return video_array
    except Exception as e:
        print(str(e))
        return 'Failed to decode video', 400

def convert_vid_to_array(video_bytes: bytes) -> np.array:
    vid_res = (480, 480) # WxH
    vid_duration = 2 # seconds
    total_output_frames = 25

    try:
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

        vid_raw, _ = process.run(input=video_bytes, capture_stdout=True)
        vid_arr = np.frombuffer(vid_raw, np.uint8).reshape((-1, vid_res[1], vid_res[0], 3))

        return vid_arr.shape

    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        raise e




def validate_db(processed):
    ## hash video
    ## check database for hash
    ## return True and result
    temp = 1

def infer_model(processes):
    temp = 1
    ## callback if not found in database
    ##  send processes video to lamda using Fast API
