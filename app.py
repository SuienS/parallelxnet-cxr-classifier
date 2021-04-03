"""
=============================================================================================
Project     : Chest X-Ray Pathology Detection and Localization using Deep Learning
Author Name : Rammuni Ravidu Suien Silva
UoW No      : 16267097
IIT No      : 2016134
Module      : Final Year Project 20/21
Supervisor  : Mr Pumudu Fernando

Prototype   : Web Interface - BackEnd [Draft: .v01]
University of Westminster, UK || IIT Sri Lanka
=============================================================================================
"""
import json
import os
from datetime import datetime

import numpy as np
# Flask Imports
from flask import Flask, request, render_template
from flask import send_file
from flask_jsglue import JSGlue
# Tensorflow Keras imports
from tensorflow.keras.models import load_model
# For secure src links
from werkzeug.utils import secure_filename

# System Library import
from lab_cxr_scripts.lab_cxr import CXRPrediction, CXRLocalization

# Model 0, 2 :- xray_labels_set[0] || Model 1 :- xray_labels_set[1]
xray_labels_set = [["Enlarged Cardiomediastinum", "Cardiomegaly", "Lung Lesion", "Lung Opacity", "Edema",
                    "Consolidation", "Pneumonia", "Atelectasis", "Pneumothorax", "Pleural Effusion",
                    "Pleural Other", "Fracture", "Support Devices"],
                   ["Nodule", "Cardiomegaly", "Emphysema", "Fibrosis", "Edema", "Consolidation", "Pneumonia",
                    "Atelectasis", "Pneumothorax", "Pleural Effusion", "Mass", "Infiltration", "Hernia",
                    "Plueral Thickening"]]

# Labels for classification tasks
xray_labels = xray_labels_set[0]
# Dependency pip install pyopenssl
# Flask Configs
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024  # Request data limited to 15MB
jsglue = JSGlue(app)

# TODO: USER GUIDE

# model load
models = [[
    load_model('models/MIMIC/PAR-64-MODEL-MIMIC-FINAL-2.h5',
               custom_objects={'weighted_loss': CXRPrediction.get_weighted_loss(1, 1)}),
    load_model('models/MIMIC/PAR-128-MODEL-MIMIC-FINAL-2.h5',
               custom_objects={'weighted_loss': CXRPrediction.get_weighted_loss(1, 1)})
], [
    load_model('models/NIH/PAR-64-MODEL-FINAL-NIH-2.h5',
               custom_objects={'weighted_loss': CXRPrediction.get_weighted_loss(1, 1)}),
    load_model('models/NIH/PAR-128-MODEL-FINAL-NIH-2.h5',
               custom_objects={'weighted_loss': CXRPrediction.get_weighted_loss(1, 1)})
]]
model = models[0]
cur_cxr_hash = 'none'

"""
==================================================================================================================
                                            Web request functions
==================================================================================================================
"""


# Web page startup
@app.route('/')
def start_web():
    return render_template("index.html")


# CXR Image upload API
@app.route('/predict/<int:model_id>', methods=['GET', 'POST'])
def upload(model_id):
    if request.method == 'POST':
        print("Model ID", model_id)

        # Selecting Model and labels set
        global model, xray_labels
        model = models[model_id % len(models)]
        xray_labels = xray_labels_set[model_id % len(xray_labels_set)]

        global cur_cxr_hash
        preds = []
        file_count = len(request.files)
        for file_num in range(file_count):
            # Getting image file from post request through the Web
            cxr_img_file = request.files['file_' + str(file_num)]
            # Generating Hash of the image file
            hashed_filename = CXRPrediction.hash_cxr(cxr_img_file)
            print(hashed_filename)
            cur_cxr_hash = hashed_filename

            # Saving the CXR image to uploads
            cxr_img_path = os.path.dirname(__file__)
            file_path = os.path.join(
                cxr_img_path, 'uploads', secure_filename(hashed_filename))
            cxr_img_file.save(file_path)

            # Detection results calculation
            preds.append(np.array(CXRPrediction.model_predict(file_path, model)[0]).tolist())

        # Final results calculation considering the results of all the uploaded images
        final_preds = np.round(np.multiply(np.mean(preds, axis=0), 100), 2)
        final_preds_max = np.round(np.multiply(np.max(preds, axis=0), 100), 2)
        final_preds_min = np.round(np.multiply(np.min(preds, axis=0), 100), 2)

        print(final_preds)
        # Creating the detection results dictionary/ JSON
        predictions_dict = {}
        for i in range(0, len(xray_labels)):
            det_rate_str = str(final_preds[i]) + "% (" + str(final_preds_max[i]) + "% - " + str(
                final_preds_min[i]) + "%)"
            predictions_dict[xray_labels[i]] = det_rate_str

        # Creating detection result JSON to be sent
        json_predictions = json.dumps(predictions_dict, indent=4)

        result = json_predictions
        return result
    return None


@app.route('/localize')
def localization():  # Localization API
    global cur_cxr_hash
    start = datetime.now()
    filepath = 'localizations/' + cur_cxr_hash.split('.')[0]

    if os.path.exists(filepath):
        file_count = len([name for name in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, name))])
        if not file_count == len(xray_labels):
            # If the localized img is already there no need to re-process
            CXRLocalization.create_cxr_localization_heatmap(cur_cxr_hash, model[len(model) - 1], xray_labels)
    else:
        # Calling Localization Function
        CXRLocalization.create_cxr_localization_heatmap(cur_cxr_hash, model[len(model) - 1], xray_labels)

    print(datetime.now() - start)
    return str(len(xray_labels))  # Returning the localized labels


# Function for sending the localized CXR image
@app.route('/get_cxr_detect_img/<int:pathology_id>')
def get_cxr_detect_img(pathology_id):
    print(pathology_id)
    global cur_cxr_hash
    localized_image_name = xray_labels[pathology_id] + '-localizedHeatmap-' + cur_cxr_hash
    filepath = 'localizations/' + cur_cxr_hash.split('.')[0] + '/'
    return send_file(filepath + localized_image_name, mimetype='image/jpg')


# Function for getting symptoms
@app.route('/get_symptoms')
def get_symptoms():
    return send_file('static/files/Symptoms.json', mimetype='application/json')


print("Server Running...")
if __name__ == '__main__':
    app.run(debug=True)  # Debugging
