from flask import Blueprint, render_template, request, flash
from .models import process_video, get_prediction


views = Blueprint('views',__name__)

@views.route('/',methods = ['GET','POST'])
def home():
    if request.method == 'POST':
        video_file = request.files.get('video')
        if not video_file:
            return 'No video file uploaded !', 400
        video_file = video_file.read()
        processed = process_video(video_file)
        flash(get_prediction(processed))

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
        processed = process_video(video_file)
        flash(get_prediction(processed))

    return render_template("Record.html")

@views.route('/healthy')
def healthy():
    # We can check the system health here 
    return 'OK', 200    