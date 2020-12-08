"""
=============================================================================
Project     : Chest X-Ray Pathology Detection using Deep Learning
Author Name : Rammuni Ravidu Suien Silva
UoW No      : 16267097
IIT No      : 2016134
Module      : Final Year Project 20/21
Supervisor  : Mr Pumudu Fernando

Prototype   : Web Interface - BackEnd [Draft: .v01]
University of Westminster, UK || IIT Sri Lanka
=============================================================================
"""
import hashlib
import json
import os

import numpy as np
from flask import Flask, request, render_template
from flask import send_file
from flask_jsglue import JSGlue
# Tensorflow Keras imports
from tensorflow.keras.applications.imagenet_utils import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename

# Labels for classification tasks
xray_labels = ["No Finding",
               "Enlarged Cardio.",
               "Cardiomegaly",
               "Lung Lesion",
               "Lung Opacity",
               "Edema",
               "Consolidation",
               "Pneumonia",
               "Atelectasis",
               "Pneumothorax",
               "Pleural Effusion",
               "Pleural Other",
               "Fracture",
               "Support Devices"]

# Flask Configs
app = Flask(__name__)
jsglue = JSGlue(app)


# Detection function
def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(320, 320))

    # Pre-processing of the input data
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)

    # Pre-processing image
    x = preprocess_input(x, mode='tf')

    preds = model.predict(x)
    return preds


# Dummy function for the model
def get_weighted_loss(x, y):
    return


# model load
model = load_model('models/mimic_then_chex_model.h5', custom_objects={'weighted_loss': get_weighted_loss(1, 1)})
cur_cxr_hash = 'none'


# Function for generating md5 of CXR image
def hash_cxr(cxr_img):
    # Generating Hash
    cxr_md5_hash = hashlib.md5()
    cxr_md5_hash.update(cxr_img.read())
    cxr_hex_hash = cxr_md5_hash.hexdigest()

    cxr_img.seek(0)  # Back to start of the file
    hashed_filename = cxr_hex_hash + '.' + cxr_img.filename.split('.')[-1]
    return hashed_filename


"""
==============================================================================
                           Web request functions
==============================================================================
"""


# Web page startup
@app.route('/')
def start_web():
    return render_template("index.html")


# CXR Image upload function
@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        global cur_cxr_hash
        # Getting image file from post request through the Web
        cxr_img_file = request.files['file']

        # Generating Hash of the image file
        hashed_filename = hash_cxr(cxr_img_file)
        print(hashed_filename)
        cur_cxr_hash = hashed_filename

        # Saving the CXR image to uploads
        cxr_img_path = os.path.dirname(__file__)
        file_path = os.path.join(
            cxr_img_path, 'uploads', secure_filename(hashed_filename))
        cxr_img_file.save(file_path)

        # Detection results calculation
        preds = model_predict(file_path, model)

        # Creating the detection results dictionary/ JSON
        predictions_dict = {}
        for i in range(0, len(xray_labels)):
            predictions_dict[xray_labels[i]] = str(preds[0][i])

        # Creating detection result JSON to be sent
        json_predictions = json.dumps(predictions_dict, indent=4)

        result = json_predictions
        return result
    return None


# Function for sending the localized CXR image
@app.route('/get_cxr_detect_img/<int:pathology_id>')
def get_cxr_detect_img(pathology_id):
    print(pathology_id)
    # use id to link to corresponding localization image TODO
    global cur_cxr_hash
    filepath = 'uploads/' + cur_cxr_hash
    return send_file(filepath, mimetype='image/jpg')


print("Server Running...")
if __name__ == '__main__':
    app.run(debug=True)  # Debugging
