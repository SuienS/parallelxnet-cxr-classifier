import hashlib
import json
import sys
import os
import glob
import re
import numpy as np

# Keras
from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from flask import send_file
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from flask_jsglue import JSGlue

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


def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(320, 320))

    # Preprocess
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    x = np.expand_dims(x, axis=0)

    # Prep
    x = preprocess_input(x, mode='tf')

    preds = model.predict(x)
    return preds


def get_weighted_loss(x, y):
    return


app = Flask(__name__)
jsglue = JSGlue(app)
model = load_model('models/mimic_then_chex_model.h5', custom_objects={'weighted_loss': get_weighted_loss(1, 1)})
cur_cxr_hash = 'none'


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        global cur_cxr_hash
        # Get file from post request through the Web
        cxr_img_file = request.files['file']

        # Generating Hash
        hashed_filename = hash_cxr(cxr_img_file)
        print(hashed_filename)
        cur_cxr_hash = hashed_filename
        # Saving the CXR image to uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(hashed_filename))
        cxr_img_file.save(file_path)

        # Prediction calculation
        preds = model_predict(file_path, model)

        predictions_dict = {}
        for i in range(0, len(xray_labels)):
            predictions_dict[xray_labels[i]] = str(preds[0][i])

        json_predictions = json.dumps(predictions_dict, indent=4)

        # Creating detection result JSON to be sent
        result = json_predictions  # Convert to string
        return result
    return None


@app.route('/get_cxr_detect_img/<int:pathology_id>')
def get_cxr_detect_img(pathology_id):
    print(pathology_id)
    global cur_cxr_hash
    filepath = 'uploads/' + cur_cxr_hash
    return send_file(filepath, mimetype='image/jpg')


def hash_cxr(cxr_img):
    # Generating Hash
    cxr_md5_hash = hashlib.md5()
    cxr_md5_hash.update(cxr_img.read())
    cxr_hex_hash = cxr_md5_hash.hexdigest()

    # Back to start of the file
    cxr_img.seek(0)
    hashed_filename = cxr_hex_hash + '.' + cxr_img.filename.split('.')[-1]
    return hashed_filename


print("running...")
if __name__ == '__main__':
    app.run(debug=True)  # Debugging
