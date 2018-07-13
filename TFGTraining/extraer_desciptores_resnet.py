'''Trains a Siamese MLP on pairs of digits from the MNIST dataset.

It follows Hadsell-et-al.'06 [1] by computing the Euclidean distance on the
output of the shared network and by optimizing the contrastive loss (see paper
for mode details).

# References

- Dimensionality Reduction by Learning an Invariant Mapping
    http://yann.lecun.com/exdb/publis/pdf/hadsell-chopra-lecun-06.pdf

Gets to 97.2% test accuracy after 20 epochs.
2 seconds per epoch on a Titan X Maxwell GPU
'''
from __future__ import absolute_import
from __future__ import print_function

from keras.preprocessing import image
from keras.models import load_model

import numpy as np
import cv2
import os
import pandas as pd

#######################################################################################################
#######################################################################################################
def create_base_network():
    # Base network to be shared (eq. to feature extraction).
    modelPath = 'resnet50_activation23.h5'
    model = load_model(modelPath)
    return model

#######################################################################################################
def extract_feats(img, model):

    media = np.array([103.939, 116.779, 123.68])  # Average from Imagenet (bgr)

    img = image.img_to_array(img)
    if img.shape != (224, 224, 3):
        print("Error: Size is not correct!")
        img = img[: , :, 0:3]
    image_bgr = img # Opencv works in bgr
    image_bgr[:, :, 0] = img[:, :, 2] - media[0]
    image_bgr[:, :, 1] = img[:, :, 1] - media[1]
    image_bgr[:, :, 2] = img[:, :, 0] - media[2]
    img = image_bgr
        
    img = np.expand_dims(img, axis=0)
    
    return model.predict(img).flatten()

#######################################################################################################

def getLabels(path, date):

	data = pd.read_csv(path + '/info.csv', header=0)
	data = np.array(data)

	data = data[data[:,0] == int(date),:]

	labels = data[:,-1]

	return labels

def loadImage(imagePath):

    img = cv2.imread(imagePath)
    img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)

    return img

def getDates(path):

    dates = []

    file = open(path + "/dates.txt")

    for line in file:
        dates.append(line[:-1])

    dates = np.sort(np.array(dates))

    return dates

#######################################################################################################
def makeBlocks(sequencePath, savePath, date, model):
    sourcePath = sequencePath + "/" + date + "/"
    images_path = os.listdir(sourcePath)

    # Calculates how many blocks of 2000 and how big the last block should be.
    n_images = len(images_path)

    # Extract features of the last block
    features = np.zeros(shape=(n_images, 50176), dtype=np.float32)
    for j in range(n_images):
        imagePath = sourcePath + images_path[j]
        img = loadImage(imagePath)
        features[j] = extract_feats(img, model)

    labels = getLabels(sequencePath,date)

    np.save(savePath + "/labels", labels)
    np.save(savePath + "/resnet_features", features)


###############################################################################################
########################### Main ##############################################################
###############################################################################################

cityPath = "../../../datasets/Boston/"
baseSavePath = "../../../datasets/BostonFeatures/"

dirs = os.listdir(cityPath)

for dir in dirs:
    if dir != ".DS_Store" and dir!= "cityInfo.txt" and dir!= "usedPanoids.txt" and dir!="extractedFeatures":
        print(dir)
        folders = os.listdir(cityPath + dir + "/")

        if ".DS_Store" in folders:
            n_sequence = len(folders) - 4
        else:
            n_sequence = len(folders) - 3

        for i in range(n_sequence):
            print(i)
            # the data, split between train and test sets
            basePath = cityPath + dir + "/sequenceSet" + str(i)

            dates = getDates(basePath)

            #input_shape = (224, 224, 3) # Input matrix size
            model = create_base_network()

            ###############################################################################
            # Extract features and save them in blocks
            ###############################################################################

            for date in dates:
                savePath = baseSavePath + dir + "/sequenceSet" + str(i) + "/" + date
                os.makedirs(savePath)
                makeBlocks(basePath, savePath,date,model)

