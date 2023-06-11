from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory
from .models import get_vid_arr_from_bytes, get_classification, get_inference, INSTANCE_ID, EC2_AZ
import hashlib
import os


views = Blueprint('views',__name__)

@views.route('/',methods = ['GET','POST'])
def home():
    if request.method == 'POST':
        vid_file = request.files.get('video')
        if not vid_file:
            return 'No video file uploaded !', 400
        vid_bytes = vid_file.stream.read()
        vid_arr = get_vid_arr_from_bytes(vid_bytes)
        flash(f"The predicted word from the video is: {get_classification(vid_arr)}")
        return redirect(url_for('views.home'))

    return render_template("Home.html")
@views.route('/Manual')
def Manual():
    return render_template("Manual.html")
@views.route('/About')
def About():
    return render_template("About.html")
@views.route('/Record',methods = ['GET', 'POST'])
def Record():
    if request.method == 'POST':
        vid_file = request.files.get('video')
        if not vid_file:
            return 'No video file uploaded !', 400
        vid_bytes = vid_file.stream.read()
        vid_arr = get_vid_arr_from_bytes(vid_bytes)
        flash(f"The predicted word from the video is: {get_classification(vid_arr)}")
        return redirect(url_for('views.Record'))
        # digest_from_inference_api = get_inference(vid_arr)
        # local_digest = hashlib.md5(vid_arr.tobytes()).hexdigest()
        # flash(f"{local_digest}\n{digest_from_inference_api}")

    return render_template("Record.html")

@views.route('/healthy')
def healthy():
    # We can check the system health here
    return 'OK', 200

@views.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(views.root_path, 'static'),
        'favicon.ico',mimetype='image/vnd.microsoft.icon')
