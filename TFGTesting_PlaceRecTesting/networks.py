from helpers import getLabels

import cv2
import numpy as np

from keras.preprocessing import image
from keras.models import load_model

# This function extracts the feature vector from every image in a path
# Inputs: Path to the images folder, number of images, season to test, neural network models
# Outputs: Feature vector with dimensions: [Descriptor size, number of images, number of compared seasons]
#          Label vector with dimensions: [Number of test images]
def extractFeatures(path, date, n_images, season, model1, model2):
    features = [] # Features for all images

    labels = getLabels(path,date)

    sequencePath = path + "/" + str(date) + "/"

    cont = 0
    #media = np.array([104.968053883,  119.316329094, 112.631406523]) # Nordland mean (bgr)
    media = np.array([103.939, 116.779, 123.68]) # Imagenet mean (bgr)
    #media = np.array([105.487823486, 113.741088867, 116.060394287]) # Places mean (bgr)
    while cont < n_images:

        path = sequencePath+str(cont)+'.png'

        img = cv2.imread(path)

        if np.shape(img) == (600,640,3):
            img = cv2.resize(img, (224,224), interpolation= cv2.INTER_AREA)


        # preprocessing of image
        img = image.img_to_array(img)
        image_bgr = img # Opencv trabaja en bgr

        # Substract mean of each color channel
        image_bgr[:, :, 0] = img[:, :, 2] - media[0]
        image_bgr[:, :, 1] = img[:, :, 1] - media[1]
        image_bgr[:, :, 2] = img[:, :, 0] - media[2]
        img = image_bgr

        img = np.expand_dims(img, axis=0) # Insert a new axis that will appear at the axis position in the expanded array shape.

        #img = preprocess_input(img)

        # Use resnet to make prediction
        feat_1 = model1.predict(img).flatten()
        feat_1 = np.reshape(feat_1, (1, 50176)) # Process image with pre trained model

        # Use added layers to create feature descriptor
        feat = model2.predict(feat_1)
        feat = np.reshape(feat, (128)) # Process vector with the added layers

        features.append(feat)

        cont = cont + 1

    return (np.asarray(features), np.asarray(labels))


# This function loads the pre-trained network (RESNET50)
def create_base_network(input_shape):
    '''Base network to be shared (eq. to feature extraction).
    '''
    MODEL_PATH = 'resnet50_activation23.h5'
    model = load_model(MODEL_PATH)
    return model

# This function loads the trained layers
def create_added_network(input_shape_2):
    '''Base network to be shared (eq. to feature extraction).
    '''
    MODEL_PATH = 'triplet_resnet23_fc_128_lr0001_std005_wd_00000005_adam_norelu_nodrop_5_epochs.h5'
    #model.load_weights(WEIGHTS_PATH, by_name=True)
    model = load_model(MODEL_PATH)
    return model