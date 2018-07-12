import numpy as np
import os
import pandas as pd

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

def getTriplet(data, neutralLabel, neutralFeaturePath):

    acceptedDistance = 15 # m
    allLabels = np.array(list(map(int, data[:,1])))

    positiveRelativeIdxs, positiveLabels, positvePaths = data[np.abs(allLabels - int(neutralLabel)) < acceptedDistance,:].T

    positiveLabels = np.array(list(map(int, positiveLabels)))
    positiveRelativeIdxs = np.array(list(map(int, positiveRelativeIdxs)))

    check1 = np.array([positvePaths == neutralFeaturePath])
    check2 = np.array([positiveLabels == int(neutralLabel)])

    check = (check1 * check2).reshape(np.shape(positiveRelativeIdxs))

    if np.sum(check) > 1:
        print("Check exceed 1. Something is properly wrong...")
        print(check)

    positvePaths = positvePaths[check == False]
    positiveRelativeIdxs = positiveRelativeIdxs[check == False]
    positiveLabels = positiveLabels[check == False]

    nPositvePaths = len(positvePaths)

    negativeRelativeIdxs, negativeLabels, negativePaths = getNegative(data, neutralLabel, acceptedDistance, nPositvePaths)

    return positiveRelativeIdxs, positiveLabels, positvePaths, negativeRelativeIdxs, negativeLabels, negativePaths

def getNegative(data, neuLabel, acceptedDistance, nPositvePaths):

    n = 0
    negativePaths = []
    negativeLabels = []
    negativeRelativeIdxs = []

    marginDistance = acceptedDistance * 10

    while n < nPositvePaths:

        randomIndex = np.random.randint(0,len(data))

        negativeRelativeIdx, negativeLabel, negativePath = data[randomIndex,:]

        if np.abs(int(neuLabel) - int(negativeLabel)) > marginDistance:

            negativePaths.append(negativePath)
            negativeLabels.append(int(negativeLabel))
            negativeRelativeIdxs.append(int(negativeRelativeIdx))
            n += 1


    return negativeRelativeIdxs, negativeLabels, negativePaths








# Method to create the indexes of the triplets
def gen_triplets_index(n_places):
    n_triplets = n_places * 38 - 2 * 38
    triplets_index = -1 * np.ones(shape=(n_triplets, 6))
    # The pairings are made with a matrix with as many rows as pairs and 2 columns
    # one with the index of the place and another with the index of the station
    index_1 = np.zeros((n_triplets, 2))  # Matrix 1 of pairing, this anger in order
    index_2 = np.zeros((n_triplets, 2))  # Matrix 2 of pairing, this will have the direction of the couple
    # We also create the matrices of opposite pairs
    index_op_1 = np.zeros((n_triplets, 2))  # Matrix 1 of pairing, this anger in order
    index_op_2 = np.zeros((n_triplets, 2))  # Matrix 2 of pairing, this will have the direction of the couple

    # We go through each row, from column to column, matching
    for place in range(n_places - 2):
        index = place * 38
        # We match the frames of the 4 stations of the same place
        index_1[index] = (place, 0)
        index_2[index] = (place, 1)

        index_1[index + 1] = (place, 0)
        index_2[index + 1] = (place, 2)

        index_1[index + 2] = (place, 0)
        index_2[index + 2] = (place, 3)

        index_1[index + 3] = (place, 1)
        index_2[index + 3] = (place, 2)

        index_1[index + 4] = (place, 1)
        index_2[index + 4] = (place, 3)

        index_1[index + 5] = (place, 2)
        index_2[index + 5] = (place, 3)

        # We match each station in that place with all of the following two
        for season in range(4):
            for i in range(2):
                for j in range(4):
                    index_1[index + 6 + season * 8 + i * 4 + j] = (place, season)
                    index_2[index + 6 + season * 8 + i * 4 + j] = (place + i + 1, j)

    # Now we do the opposite
    # We go through each row, from column to column, unpairing
    for place in range(n_places - 2):
        indice = place * 38
        # We match the frames randomly, 11 far and 11 close
        # The opposing couples can be above or below the place so
        # you have to calculate the random place differently
        for i in range(38):
            if (i < 38 / 2):
                index_op_1[indice + i] = (place, np.random.randint(0, 3))
                index_op_2[indice + i] = (lugarContrario(place, n_places, 0), np.random.randint(0, 3))
            else:
                index_op_1[indice + i] = (place, np.random.randint(0, 3))
                index_op_2[indice + i] = (lugarContrario(place, n_places, 1), np.random.randint(0, 3))

    # We mix the positive and negative matrices equally
    indices_mezclados = np.arange(n_triplets)
    np.random.shuffle(indices_mezclados)
    # We create matrices for mixed indices
    indices_1_mezc = np.zeros((n_triplets, 2))
    indices_2_mezc = np.zeros((n_triplets, 2))
    indices_op_2_mezc = np.zeros((n_triplets, 2))
    # We mix the indices
    indices_1_mezc = index_1[indices_mezclados]
    indices_2_mezc = index_2[indices_mezclados]
    indices_op_2_mezc = index_op_2[indices_mezclados]

    triplets_index[:, 0] = indices_1_mezc[:, 0]
    triplets_index[:, 1] = indices_1_mezc[:, 1]

    triplets_index[:, 2] = indices_2_mezc[:, 0]
    triplets_index[:, 3] = indices_2_mezc[:, 1]

    triplets_index[:, 4] = indices_op_2_mezc[:, 0]
    triplets_index[:, 5] = indices_op_2_mezc[:, 1]

    return triplets_index.astype(int)


# Function to look for the opposite partner in an interval above and below
# of that place, with a window of 5 (2 places above and below)
def lugarContrario(lugar, n_lugares, lejos):
    lugar_contrario = 0
    if lugar < 50:
        # We search between 3 following places and the last place or 100 after
        if lejos:
            lugar_contrario = np.random.randint(lugar + 3, n_lugares - 1)
        else:
            lugar_contrario = np.random.randint(lugar + 3, lugar + 100)

    elif (lugar > n_lugares - 50):
        # We search between 3 previous places and the initial place
        if lejos:
            lugar_contrario = np.random.randint(0, lugar - 3)
        else:
            lugar_contrario = np.random.randint(lugar - 100, lugar - 3)
    else:
        # We search between the initial and 3 before, 3 after and the end
        # The decision of whether to search before or after is random
        antes = np.random.randint(0, 1)
        # We also consider if we look for the whole range or only near the position
        if lejos:
            if antes:
                lugar_contrario = np.random.randint(0, lugar - 3)
            else:
                lugar_contrario = np.random.randint(lugar + 3, n_lugares - 1)
        else:
            if antes:
                # We prevent it from moving beyond the initial index in the first 100 data
                alejado = np.array([0, lugar - 3 - 100])
                alejado = alejado.max()
                lugar_contrario = np.random.randint(alejado, lugar - 3)
            else:
                alejado = np.array([lugar + 100, n_lugares - 1])
                alejado = alejado.min()
                lugar_contrario = np.random.randint(lugar + 3, alejado)

    return lugar_contrario
