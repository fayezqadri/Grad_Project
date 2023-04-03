from flask import Blueprint, render_template, request, flash
from .models import process_video, validate_db, infer_model
import numpy as np
import cv2

views = Blueprint('views',__name__)

@views.route('/',methods = ['GET','POST'])
def home():
    if request.method == 'POST':
        video_file = request.files.get('video')
        if not video_file:
            return 'No video file uploaded !', 400
        video_file = video_file.read()
        processed = process_video(video_file)
        flash(processed.shape)
        #processed = process_video
        
        #python main.py
        # print(processed)
    #     db_dict = validate_db(processed)
    #     if (db_dict[0]==False):
    #         infer_model(processed)
    return render_template("Home.html")
@views.route('/Manual')
def Manual():
    return render_template("Manual.html")
@views.route('/About')
def About():
    return render_template("About.html")
@views.route('/Record',methods = ['GET','POST'])
def Record():

    if request.method == 'POST':
        video_file = request.files.get('video')
        if not video_file:
            flash("No video Ile Found !")
            return 'No video file uploaded !', 400
        else:
            processed = process_video(video_file)
            flash(processed.shape)
    # if request.method == 'POST':
    #     video = request.form
    #     processed = process_video(video)
    #     db_dict = validate_db(processed)
    #     if (db_dict[0]==False):
    #         infer_model(processed)
    return render_template("Record.html")
