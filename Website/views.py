from flask import Blueprint, render_template, request, flash

views = Blueprint('views',__name__)

@views.route('/',methods = ['GET','POST'])
def home():
    # if request.method == 'POST':
    #     video = request.form
    if (False):
        flash("Video Found in database and print result.", category='predicted_before')
    if(False):
        flash("Here is the prediction of our model.",category="model_prediction")

    return render_template("Home.html")
@views.route('/Manual')
def Manual():
    return render_template("Manual.html")
@views.route('/About')
def About():
    return render_template("About.html")
@views.route('/Record')
def Record():
    return render_template("Record.html")
