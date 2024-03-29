import hashlib

import numpy as np
import tensorflow as tf
# Display
from PIL import Image
# Tensorflow Keras imports
from tensorflow.keras import preprocessing
from tensorflow.keras.applications.imagenet_utils import preprocess_input
from tensorflow.keras.preprocessing import image


# Detection function
def model_predict(img_path, model):
    img = Image.open(img_path)
    img_crop_box = img.getbbox()

    # Auto cropping the unwanted areas
    cropped = img.crop(img_crop_box)
    cropped.save(img_path)

    # Resizing image to 320*320
    img = image.load_img(img_path, target_size=(320, 320))

    # Pre-processing of the input data
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)

    # Normalizing and centering of the pixel values of the image
    x = preprocess_input(x, mode='tf')

    # Test time augmentation
    x_f = tf.image.flip_left_right(x)

    # Averaging the outputs of the multiple models
    preds_0, preds_1, preds_0_e, preds_1_e = 0, 0, 0, 0
    for s_model in model:
        preds_0 = s_model.predict(x)
        preds_0_e = np.add(preds_0, preds_0_e)
        preds_1 = s_model.predict(x_f)
        preds_1_e = np.add(preds_1, preds_1_e)

    preds_0_e /= len(model)
    preds_1_e /= len(model)

    # Final Result Calculation
    preds = np.add(preds_0_e, preds_1_e) / 2
    return preds


# Dummy function for the model
def get_weighted_loss(x, y):
    return x + y


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
