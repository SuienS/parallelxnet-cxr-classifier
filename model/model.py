from tensorflow.keras import backend as K
from tensorflow.keras.applications.densenet import DenseNet121
from tensorflow.keras.applications.densenet import DenseNet169
# Model Imports
from tensorflow.keras.applications.resnet_v2 import ResNet50V2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Multiply, Concatenate, Input
from tensorflow.keras.models import Model


# Parallelize Custom Block
def parallelize_block(tensor, ratio=128):
    nb_channel = K.int_shape(tensor)[-1]

    # Averaging
    x = GlobalAveragePooling2D()(tensor)
    x = Dense(nb_channel // ratio, activation='relu')(x)
    x = Dense(nb_channel, activation='sigmoid')(x)

    # Weighting
    x = Multiply()([tensor, x])
    return x


# MAIN MODEL
def ParallelXNet(n_classes, tau=128, input_shape=(320, 320, 3), weights='imagenet', output_activation="sigmoid"):
    # Combined Input
    combinedInput = Input(batch_shape=(None, None, None, 3))

    # Base models preoaded with imagenet weights
    resnetV2_m = ResNet50V2(weights=weights, include_top=False,
                            input_shape=input_shape, input_tensor=combinedInput)
    densenet121_m = DenseNet121(weights=weights, include_top=False,
                                input_shape=input_shape, input_tensor=combinedInput)
    densenet169_m = DenseNet169(weights=weights, include_top=False,
                                input_shape=input_shape, input_tensor=combinedInput)

    for layer in resnetV2_m.layers:
        layer._name = layer.name + str("_0")

    for layer in densenet121_m.layers:
        layer._name = layer.name + str("_1")

    for layer in densenet169_m.layers:
        layer._name = layer.name + str("_2")

    base_model_output = [
        resnetV2_m.output,
        densenet121_m.output,
        densenet169_m.output
    ]

    # Concatenating the models
    c_model = Concatenate()(base_model_output)

    # Passing via parallelize block
    par_c_model = parallelize_block(
        tensor=c_model,
        ratio=tau
    )

    # Final Average Pooling layer
    x = GlobalAveragePooling2D()(par_c_model)

    # Final Dense Layer
    detection_output = Dense(n_classes, activation=output_activation)(x)

    return Model(inputs=combinedInput, outputs=detection_output)
