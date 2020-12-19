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
import hashlib
import json
import os
from datetime import datetime

import numpy as np
# Display
from PIL import Image
from flask import Flask, request, render_template
from flask import send_file
from flask_jsglue import JSGlue
from matplotlib.cm import get_cmap
from tensorflow import GradientTape, reduce_mean
from tensorflow.keras import preprocessing
from tensorflow.keras.applications.imagenet_utils import preprocess_input
# Tensorflow Keras imports
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.python.keras import Model, Input
# For secure src links
from werkzeug.utils import secure_filename

# Labels for classification tasks
xray_labels = ["Enlarged Cardiomediastinum",
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

    # Normalizing and centering of the pixel values of the image
    x = preprocess_input(x, mode='tf')

    preds = model.predict(x)
    return preds


# Dummy function for the model
def get_weighted_loss(x, y):
    return


# model load
# model = load_model('models/mimic_then_chex_model.h5', custom_objects={'weighted_loss': get_weighted_loss(1, 1)})
model = load_model('models/MultiDenseWithResnet-par-mimic.h5',
                   custom_objects={'weighted_loss': get_weighted_loss(1, 1)})
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


def generate_cxr_img_array(img_path, size):
    cxr_img = preprocessing.image.load_img(img_path, target_size=size)

    cxr_img_array = preprocessing.image.img_to_array(cxr_img)

    # Expanding the dimensions
    cxr_img_array = np.expand_dims(cxr_img_array, axis=0)
    return cxr_img_array


# Generating detection heatmap using Grad-CAM technique
# Selvaraju, R.R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., Batra, D., 2020.
# Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization. Int J Comput Vis 128, 336–359.
# https://doi.org/10.1007/s11263-019-01228-7
def generate_detection_heatmap(
        img_array, model, end_conv_layer_name, classifier_layer_names
):
    # New  model linking the original model's inputs to the last convolutional layer
    end_conv_layer = model.get_layer(end_conv_layer_name)
    end_conv_layer_model = Model(model.inputs, end_conv_layer.output)

    # Second model mapping the activation of the last convolutional layer to the final dense layer
    classifier_layer_input = Input(shape=end_conv_layer.output.shape[1:])
    x = classifier_layer_input
    for layer_name in classifier_layer_names:
        x = model.get_layer(layer_name)(x)
    temp_classifier_model = Model(classifier_layer_input, x)

    heatmaps = []  # Holds the detection_heatmap info for each pathology

    # Iterating through all the pathologies to generate detection_heatmap for each
    for pathology_index in range(0, len(xray_labels)):
        # Gradient calculation of the predicted classes for the provided input relative to the output activations of the
        # last convolutional layer
        with GradientTape() as tape:
            # Generating the activations of the end convolutional layer of the model
            end_conv_layer_output = end_conv_layer_model(img_array)
            tape.watch(end_conv_layer_output)  # Keeps records of the generation of the activations

            # Calculating the output for each 'pathology_index'
            preds = temp_classifier_model(end_conv_layer_output)
            seletcted_class_channel = preds[:, pathology_index]

        # Gradient of the selected class_index
        class_grads = tape.gradient(seletcted_class_channel, end_conv_layer_output)

        # Vectorization of the generated gradients
        pooled_class_grads = reduce_mean(class_grads, axis=(0, 1, 2))

        # Weighting the calculated channel output values by its contribution towards the considered class
        end_conv_layer_output = end_conv_layer_output.numpy()[0]
        pooled_class_grads = pooled_class_grads.numpy()
        for i in range(pooled_class_grads.shape[-1]):
            end_conv_layer_output[:, :, i] *= pooled_class_grads[i]

        # Calculating the mean across the activation of channels to generate the final detection_heatmap
        detection_heatmap = np.mean(end_conv_layer_output, axis=-1)

        # Normalizing the generated heatmap to 0 - 1 to make it possible for colourized illustration
        detection_heatmap = np.maximum(detection_heatmap, 0) / np.max(detection_heatmap)
        heatmaps.append(detection_heatmap)  # appending to the heatmap list

    return heatmaps


def create_cxr_localization_heatmap(cxr_hash, last_conv_layer_name="concatenate",
                                    classifier_layer_names=None):
    if classifier_layer_names is None:  # mutable argument
        classifier_layer_names = [
            "global_average_pooling2d_1",
            "dense_2",
        ]
    cxr_img_path = './uploads/' + cxr_hash

    # Preparing input cxr image - Resizing and Normalizing
    img_array = preprocess_input(generate_cxr_img_array(cxr_img_path, size=(320, 320)), mode='tf')

    # Generating class activation based heatmap
    heatmaps = generate_detection_heatmap(
        img_array, model, last_conv_layer_name, classifier_layer_names
    )

    # Iterating through all the pathologies to generate detection_heatmap for each
    for pathology_index in range(0, len(xray_labels)):
        heatmap = heatmaps[pathology_index]
        cxr_img = preprocessing.image.load_img(cxr_img_path)
        cxr_img = preprocessing.image.img_to_array(cxr_img)

        # Scaling the heatmap values to be in range 0 - 255
        heatmap = np.uint8(255 * heatmap)

        # Colorizing the heatmap
        colormap = get_cmap("jet")  # Using jet colormap

        # RGB values of the generated colormap
        cm_colors = colormap(np.arange(256))[:, :3]
        detection_heatmap = cm_colors[heatmap]

        # Creating the image with colorized (RGB) heatmap
        detection_heatmap = preprocessing.image.array_to_img(detection_heatmap)
        detection_heatmap = detection_heatmap.resize((cxr_img.shape[1], cxr_img.shape[0]), Image.ANTIALIAS)
        detection_heatmap = preprocessing.image.img_to_array(detection_heatmap)

        # Superimpose the heatmap onto the original unprocessed cxr image
        superimposed_img = detection_heatmap * 0.4 + cxr_img
        superimposed_img = preprocessing.image.array_to_img(superimposed_img)

        org_cxr_image = Image.open(cxr_img_path)
        org_3d_cxr_image = np.tile(np.array(org_cxr_image)[:, :, None], [1, 1, 3])  # 3-Channel original input cxr image

        # Save path for the generated heatmap image
        localized_image_name = xray_labels[pathology_index] + '-localizedHeatmap-' + cxr_hash
        file_path = './localizations/' + cxr_hash.split('.')[0] + '/'

        # Make the directory if not exists
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        Image.fromarray(
            np.hstack((org_3d_cxr_image, np.array(superimposed_img)))
        ).save(file_path + localized_image_name)


"""
========================================================================================================
                                        Web request functions
========================================================================================================
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

        start = datetime.now()
        # for i in range(0, len(xray_labels)):
        create_cxr_localization_heatmap(hashed_filename)

        print(datetime.now() - start)

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
    global cur_cxr_hash
    localized_image_name = xray_labels[pathology_id] + '-localizedHeatmap-' + cur_cxr_hash
    filepath = 'localizations/' + cur_cxr_hash.split('.')[0] + '/'
    return send_file(filepath + localized_image_name, mimetype='image/jpg')


print("Server Running...")
if __name__ == '__main__':
    app.run(debug=True)  # Debugging
