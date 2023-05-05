from flask import Blueprint, render_template, request, flash
from .models import get_vid_arr_from_bytes, get_classification, get_inference
import hashlib


views = Blueprint('views',__name__)

@views.route('/',methods = ['GET','POST'])
def home():
    if request.method == 'POST':
        video_file = request.files.get('video')
        if not video_file:
            return 'No video file uploaded !', 400
        video_file = video_file.read()
        processed = get_vid_arr_from_bytes(video_file)
        flash(get_classification(processed))

    return render_template("Home.html")
@views.route('/Manual')
def Manual():
    return render_template("Manual.html")
@views.route('/About')
def About():
    return render_template("About.html")
@views.route('/Record',methods = ['GET', 'POST'])
def Record():
    print('enter record')
    if request.method == 'POST':
        video_file = request.files.get('video')
        if not video_file:
            return 'No video file uploaded !', 400
        video_file = video_file.read()
        vid_arr = get_vid_arr_from_bytes(video_file)
        # flash(get_classification(vid_arr))
        digest_from_inference_api = get_inference(vid_arr)
        local_digest = hashlib.md5(vid_arr.tobytes()).hexdigest()
        flash(f"{local_digest}\n{digest_from_inference_api}")

    return render_template("Record.html")

@views.route('/healthy')
def healthy():
    # We can check the system health here
    return 'OK', 200
