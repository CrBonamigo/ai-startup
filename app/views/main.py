from flask import render_template, jsonify, Flask, redirect, url_for, request
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES
from app import app
import random
import os
from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
from app.src.image_emotion_gender import runDetector

#app = Flask(__name__, template_folder='templates')

photos = UploadSet('photos', IMAGES, default_dest=lambda app: os.path.join(os.getcwd(), 'app/static/img_up'))
configure_uploads(app, (photos, ))
image_storage_path = os.path.join(os.getcwd(), 'app/static/img_up')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/uploaded', methods = ['GET', 'POST'])
def upload_file():
	if request.method == 'POST' and 'photo' in request.files:
		filename = photos.save(request.files['photo'])
		image_location = os.path.join(image_storage_path, filename)
		woman, man, filename_save = runDetector(image_location, filename)
		people_counting = man+ woman
		#return filename
	return render_template('uploaded.html', image_name=filename, image_location=image_location, people_counting=people_counting, man=man, woman=woman, filename_save=filename_save)

	

@app.route('/appml')
def appml():
    return render_template('appml.html', title='Applications')
    
@app.route('/face')
def face():
    return render_template('face.html')


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')
	
@app.route('/cancel')
def cancel():
    return 'You cancel payment'
	
@app.route('/success')
def success():
    return 'Payment success'
    
