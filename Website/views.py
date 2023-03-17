from flask import Blueprint, render_template, request, flash
from .models import process_video, validate_db, infer_model

views = Blueprint('views',__name__)

@views.route('/',methods = ['GET','POST'])
def home():
    # if request.method == 'POST':
    #     video = request.form
    #     processed = process_video(video)
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
    # if request.method == 'POST':
    #     video = request.form
    #     processed = process_video(video)
    #     db_dict = validate_db(processed)
    #     if (db_dict[0]==False):
    #         infer_model(processed)
    return render_template("Record.html")
