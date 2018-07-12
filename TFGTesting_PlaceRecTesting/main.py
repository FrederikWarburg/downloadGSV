'''
This program test the performance of a neural network model as a feature
extraction method for place recognition.


This script should run without any changes on my data. However, you'll need to make some changes to make it run for your data...

'''

from networks import create_base_network, create_added_network
from distanceFunctions import closestPlaces
from helper2 import getClosestReferenceLabels, getImageByLabel, loadImages
from networks2 import extractFeatures2
import numpy as np
import os
import matplotlib.pyplot as plt

###############
# Load data (You will need to change this - to fit you data)
# Format you images such that their dimensions are (224,224,3)
###############

# PATH OF THE IMAGES (change the path)
city = "London"

cityPath = city + "/"
dirs = os.listdir(cityPath)
dirs = dirs[1:] # Used to skip a default folder on mac called .DS_Store (not sure if you have that one)

# The script only compares two images. I have 4 images from the same place. Therefore, I have to chose which two time-stamps
# I want to use for comparison. If you only have 2 time-stamps, then this shouldn't be used.
ref = 0 # olderst
inp = 3 # newest

print("Load images")
# You will have to change this function such that it fits your data.
# It should load you data: Images and Labels (dates are probably not relevant in your case).
imInput, labelInput, datesInput, imRefs, labelRefs, datesRefs = loadImages(dirs, city, inp, ref)

# PARAMETERS: (change test size if you don't want to test on all your data)
test_size = len(labelRefs)

###############
# Model loading  (nothing needs to be changed here)
###############

print("Load models")
input_shape = (224, 224, 3)  # Pre-trained model input size
model1 = create_base_network(input_shape)
input_shape2 = (50176,)  # Added model input size
model2 = create_added_network(input_shape2)

####################
# Feature extraction (nothing needs to be changed here)
####################

print("Extract Features")
# Dimensions: [number of images, Dimension descriptor], [number of images]
inputFeatures = extractFeatures2(imInput, model1, model2)
referenceFeatures = extractFeatures2(imRefs, model1, model2)

####################
#               Change the way you calculate accuracy
# Evaluation (I think your trueLabels == your labelRefs. In my case I cannot be sure, but if you images are aligned they should be the same.
#              Let me know if this is confusing. )
####################
print("Evaluate results")
trueLabels = getClosestReferenceLabels(labelInput, labelRefs)

prediction = []
distances = []

# Loop in which we walk the base that we take to test, comparing each image with the reference.
for i in range(test_size):

    # We find closest places based on euclidian distance
    closest_places_labels, distances_to_places = closestPlaces(inputFeatures[i], referenceFeatures, labelRefs, 5)

    # I only chose to save the closest place. You can get more information, if you save more information.
    # It is very normal to use a knn search here. E.g by saving the 5 nearest neighbors you will be able to evaluate if it would
    # give you a higher accuracy to use 1,2,3,4,5 nearest neighbors.
    prediction.append(closest_places_labels[0])
    distances.append(distances_to_places[0])

# Calculate accuracy for sequence (Should be changed)
# I accept a prediction if it is close (label distance is less than 30). If your images are well aligned you would problaly
# only accept a prediciton if the label distance is 0 or 1.
accuracy = np.round(np.sum(np.abs(np.array(prediction) - np.array(trueLabels)) < 30) / len(prediction), 3)

####################
# We make statistics (You can comment this out. It is a way to illustrate the results visually)
####################

print("Accuracy of this path is ", accuracy)
print("Number of reference images ", len(imRefs))

# This should probably also be change to fit your data.
predictionImages, predictionDates = getImageByLabel(imRefs, labelRefs, prediction, datesRefs)
trueImages, trueDates = getImageByLabel(imRefs, labelRefs, trueLabels, datesRefs)

print("Plot results")
for inputIm, inputLabel, inputDate, predIm, predLabel, predDate, trueIm, trueLabel, trueDate in zip(imInput,labelInput, datesInput,
                                                                                                    predictionImages,prediction, predictionDates,
                                                                                                    trueImages,trueLabels, trueDates):
    plt.figure(figsize=(15, 5))
    plt.subplot(1, 3, 1)
    plt.title('Input label: ' + str(inputLabel) + '\n Taken ' + inputDate)
    plt.axis('off')
    plt.imshow(inputIm)

    plt.subplot(1, 3, 2)
    plt.title('Prediction label: ' + str(predLabel) + '\n Taken ' + predDate)
    plt.axis('off')
    plt.imshow(predIm)

    plt.subplot(1, 3, 3)
    plt.title('Closest label: ' + str(trueLabel) + '\n Taken ' + trueDate)
    plt.axis('off')
    plt.imshow(trueIm)

    plt.show()

