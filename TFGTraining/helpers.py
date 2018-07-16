import numpy as np
import os
import pandas as pd

from getHardNegatives import getNHardNegative

def getDatesByFolderNames(path):

    dates = []

    folders = os.listdir(path)

    for folder in folders:
        if folder != ".DS_Store":
            dates.append(folder)

    dates = np.sort(np.array(dates))

    return dates


def getAllFeatures(cityPath):

    notPathFolders = ['.DS_Store', 'cityInfo.txt', 'usedPanoid.txt']
    paths = os.listdir(cityPath)

    allFeatures = []
    allLabels = []
    uniqueID = []

    counter = 0

    for path in paths:
        if path not in notPathFolders:

            folders = os.listdir(cityPath + "/" + path)
            notImageFolders = ['.DS_Store', 'description.json', 'overview.json','overview_map.html']

            for folder in folders:
                if folder not in notImageFolders:

                    sequenceSet = cityPath + path + "/" + folder

                    dates = getDatesByFolderNames(sequenceSet)

                    for date in dates:

                        featureFolderPath = sequenceSet + "/" + date

                        fullPathFeatures = featureFolderPath + "/resnet_features.npy"
                        fullPathLabels = featureFolderPath + "/labels.npy"
                        #feature = np.load(fullPathFeatures)
                        labels = np.load(fullPathLabels)

                        uniqueID.append(counter)
                        allFeatures.append(fullPathFeatures)
                        allLabels.append(labels)

    allLabels = np.array(allLabels)

    data = np.array([allLabels,allFeatures]).T

    return data


def formatData(data):

    allLabels = []
    allPaths = []
    allRelativeIdx = []

    for i in range(len(data[:,1])):

        labels = data[i,0]
        path = data[i,1]

        for j, label in enumerate(labels):

            allLabels.append(label)
            allPaths.append(path)
            allRelativeIdx.append(j)

    data = np.array([allRelativeIdx,allLabels,allPaths]).T

    return data

def getFeatures(sequenceSet):

    dates = getDatesByFolderNames(sequenceSet)

    allFeatures = []
    allLabels = []

    for date in dates:

        featureFolderPath = sequenceSet + "/" + date

        fullPathFeatures = featureFolderPath + "/resnet_features.npy"
        fullPathLabels = featureFolderPath + "/labels.npy"
        feature = np.load(fullPathFeatures)
        labels = np.load(fullPathLabels)

        allFeatures.append(feature)
        allLabels.append(labels)

    return allLabels, allFeatures


def getFeaturePaths(basePath):

    fullFeaturePaths = {}
    fullCSVPaths = {}
    counter = 0

    folders = os.listdir(basePath)
    notImageFolders = ['.DS_Store', 'description.json', 'overview.json','overview_map.html']

    for folder in folders:
        if folder not in notImageFolders:

            sequenceSetPath = basePath + "/" + folder
            dates = getDatesByFolderNames(sequenceSetPath)

            allfeatures = []

            for date in dates:

                featurePath = sequenceSetPath + "/" + date
                features = os.listdir(featurePath)

                for feature in features:
                    allfeatures.append(feature)


            fullFeaturePaths[str(counter)] = allfeatures
            fullCSVPaths[str(counter)] = sequenceSetPath + "/info.csv"
            counter += 1

    return fullFeaturePaths, fullCSVPaths

def compute_accuracy(y_true, y_pred):
    '''Compute classification accuracy with a fixed threshold on distances.
    '''
    pred = y_pred.ravel() < 0.5
    return np.mean(pred == y_true)


def getBatch(positiveRelativeIdxs,positvePaths,neutralFeature, negativeRelativeIdxs,negativePaths, batchSize, inputSize):

    batch = np.zeros(shape=(batchSize, 3, inputSize), dtype=np.float32)
    weights = np.ones(shape=(batchSize), dtype=np.uint8)

    batchIndex = 0

    # total number of triplet combinations get n positive and n negative features
    for positiveRelativeIdx, positivePath in zip(positiveRelativeIdxs,positvePaths):

        positiveFeature = loadFeature(positivePath, positiveRelativeIdx)

        for negativeRelativeIdx, negativePath in zip(negativeRelativeIdxs,negativePaths):

            negativeFeature = loadFeature(negativePath, negativeRelativeIdx)

            batch[batchIndex, 0] = positiveFeature
            batch[batchIndex, 1] = neutralFeature
            batch[batchIndex, 2] = negativeFeature

            batchIndex += 1

    return batch, weights


def loadFeature(path, relativeIdx):

    feature = np.load(path)

    feature = feature[int(relativeIdx),:]

    return feature

def getTriplet(data, neutralLabel,neutralFeaturePath, neutralRelativeIdx):

    acceptedDistance = 15 # m
    allLabels = np.array(list(map(int, data[:,1])))

    positiveRelativeIdxs, positiveLabels, positvePaths = data[np.abs(allLabels - int(neutralLabel)) < acceptedDistance,:].T

    positiveLabels = np.array(list(map(int, positiveLabels)))
    positiveRelativeIdxs = np.array(list(map(int, positiveRelativeIdxs)))

    check1 = np.array([positvePaths == neutralFeaturePath])
    check2 = np.array([positiveLabels == int(neutralLabel)])

    check = (check1 * check2).reshape(np.shape(positiveRelativeIdxs))

    positvePaths = positvePaths[check == False]
    positiveRelativeIdxs = positiveRelativeIdxs[check == False]
    positiveLabels = positiveLabels[check == False]

    nPositvePaths = len(positvePaths)

    #negativeRelativeIdxs, negativeLabels, negativePaths = getNegative(data, neutralLabel, acceptedDistance, nPositvePaths)
    #negativeRelativeIdxs, negativeLabels, negativePaths = getHardNegative(data, neutralLabel, acceptedDistance, nPositvePaths, allLabels)
    #difficulty = 7 # in avg we look 10x the images we need to obtain the negatives we need.
    difficulty = 2
    negativeRelativeIdxs, negativeLabels, negativePaths = getNHardNegative(data, neutralLabel,neutralFeaturePath, neutralRelativeIdx, allLabels, nPositvePaths,difficulty)

    return positiveRelativeIdxs, positiveLabels, positvePaths, negativeRelativeIdxs, negativeLabels, negativePaths