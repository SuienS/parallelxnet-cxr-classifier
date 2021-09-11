import os

import numpy as np
# Display
from PIL import Image
from matplotlib.cm import get_cmap
# Tensorflow Keras imports
from tensorflow import GradientTape, reduce_mean
from tensorflow.keras import preprocessing
from tensorflow.keras.applications.imagenet_utils import preprocess_input
from tensorflow.python.keras import Model, Input

# System library
from lab_cxr_scripts.lab_cxr import CXRPrediction


# Localization Algorithm is ADAPTED and MODIFIED from blow referenced paper
# Selvaraju, R.R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., Batra, D., 2020.
# Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization. Int J Comput Vis 128, 336–359.
# https://doi.org/10.1007/s11263-019-01228-7
def generate_detection_heatmap(
        img_array, model, xray_labels, end_conv_layer_name, classifier_layer_names
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

        # Normalizing the generated heatmap to 0 - 1 to make it possible for colorized illustration
        detection_heatmap = np.maximum(detection_heatmap, 0) / np.max(detection_heatmap)
        heatmaps.append(detection_heatmap)  # appending to the heatmap list

    return heatmaps


def create_cxr_localization_heatmap(cxr_hash, model, xray_labels, last_conv_layer_name="concatenate",
                                    classifier_layer_names=None):
    if classifier_layer_names is None:  # mutable argument
        classifier_layer_names = [
            "global_average_pooling2d_1",
            "dense_2",
        ]
    cxr_img_path = './uploads/' + cxr_hash

    # Preparing input cxr image - Resizing and Normalizing
    img_array = preprocess_input(CXRPrediction.generate_cxr_img_array(cxr_img_path, size=(320, 320)), mode='tf')

    # Generating class activation based heatmap
    heatmaps = generate_detection_heatmap(
        img_array, model, xray_labels, last_conv_layer_name, classifier_layer_names
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

        org_cxr_image = Image.open(cxr_img_path).convert('L')
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
