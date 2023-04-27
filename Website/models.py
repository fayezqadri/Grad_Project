import boto3
import numpy as np
import hashlib
import ffmpeg

LAMBDA_ENDPOINT_URL = "/"
VID_RES = (480, 480)
VID_DURATION = 2
TOTAL_OUTPUT_FRAMES = 25

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


def process_video(video_bytes):
    try:
        vid_raw, _ = process.run(input=video_bytes, capture_stdout=True)
        vid_arr = np.frombuffer(vid_raw, np.uint8).reshape((-1, VID_RES[1], VID_RES[0], 3))

        return vid_arr
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        raise e

table_name = os.environ.get('TABLE_NAME')
def get_prediction(processed):

    processed = np.random.rand(24,240,240,3)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    processed_bytes = processed.tobytes()
    hash_video = hashlib.md5(processed_bytes)
    hash_video = hash_video.hexdigest()
    response = table.get_item(Key={'hash_key': hash_video})

    if 'Item' in response:
        # The hash exists in the table, return the value
        return response['Item']['value']
    else:
        #### Send processed to FAST- API
        pred = 1

        table.put_item(Item={'hash_key': hash_video, 'value': pred })

        return pred





def validate_db(processed):
    ## hash video
    ## check database for hash
    ## return True and result
    temp = 1

def infer_model(processes):
    temp = 1
    ## callback if not found in database
    ##  send processes video to lamda using Fast API
