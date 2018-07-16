import imagehash
import cv2
import numpy as np
from PIL import Image

from distanceFunctions import hamming2

def getNHardNegative(data, anchorLabel, allLabels,nPositives,difficulty):
    # This method use the average hashing to get similar images.
    anchorLabel = int(anchorLabel)

    anchorIdx = allLabels.index(anchorLabel)
    anchorRelativeIdx, anchorLabel, anchorPath = data[anchorIdx, :].T

    a = anchorPath.find("Features")

    anchorImagePath = anchorPath[0:a] + anchorPath[a+len("Features"):]
    anchorImage = Image.fromarray(cv2.imread(anchorImagePath))
    anchorImageHash = imagehash.average_hash(anchorImage, 8)

    negativePaths = []
    negativeLabels = []
    negativeRelativeIdxs = []
    usedNegativeIndexes = [] # To avoid we do not have the same negative in batch.

    numberOfNegatives = 0

    while numberOfNegatives < nPositives:

        randomIdx = np.random.randint(0, len(allLabels))

        # To avoid we do not have the same negative in batch.
        if randomIdx not in usedNegativeIndexes:

            negativeRelativeIdx, negativeLabel, negativePath = data[randomIdx, :].T

            # random label should be far from anchor label to make sure it is not the same place.
            if np.abs(negativeLabel-anchorLabel) > 100:

                negativeImagePath = negativePath[0:a] + negativePath[a + len("Features"):]
                negativeImage = Image.fromarray(cv2.imread(negativeImagePath))
                negativeImageHash = imagehash.average_hash(negativeImage, 8)

                dist = hamming2(str(anchorImageHash),str(negativeImageHash))

                # The negative images should be similar to the anchor image, but not too similar.
                if dist < difficulty:

                    negativePaths.append(negativePath)
                    negativeLabels.append(int(negativeLabel))
                    negativeRelativeIdxs.append(int(negativeRelativeIdx))
                    usedNegativeIndexes.append(randomIdx)

                    numberOfNegatives += 1

    return negativeRelativeIdxs, negativeLabels, negativePaths


def getNegative(data, neuLabel, acceptedDistance, nPositvePaths):
    # This method get completely random negatives
    n = 0
    negativePaths = []
    negativeLabels = []
    negativeRelativeIdxs = []

    marginDistance = acceptedDistance * 10

    while n < nPositvePaths:

        randomIndex = np.random.randint(0, len(data))

        negativeRelativeIdx, negativeLabel, negativePath = data[randomIndex, :]

        if np.abs(int(neuLabel) - int(negativeLabel)) > marginDistance:
            negativePaths.append(negativePath)
            negativeLabels.append(int(negativeLabel))
            negativeRelativeIdxs.append(int(negativeRelativeIdx))
            n += 1

    return negativeRelativeIdxs, negativeLabels, negativePaths


def getHardNegative(data, neuLabel, acceptedDistance, nPositivePaths, allLabels):
    # This method use prior knowledge and get images that are close in lat and lon
    n = 0
    counter = 0
    neuLabel = int(neuLabel)

    negativePaths = []
    negativeLabels = []
    negativeRelativeIdxs = []
    usedNegativeIndexes = []

    minLag = 2
    maxLag = 15

    # This will ensure that our negative is close to our positive and thus we will get some hard negatives. Hopefully they wont be too hard bc then we will risk to be stuck in local minima.
    marginDistance = acceptedDistance * minLag
    minDistance = neuLabel - (acceptedDistance * maxLag)
    maxDistance = neuLabel + (acceptedDistance * maxLag)

    while n < nPositivePaths:

        counter += 1
        randomLabel = np.random.randint(minDistance, maxDistance)

        index = np.argmin(np.abs(allLabels - int(randomLabel)))

        if index == list():
            index = index[0]

        negativeRelativeIdx, negativeLabel, negativePath = data[index, :].T

        if index not in usedNegativeIndexes:

            if np.abs(neuLabel - int(negativeLabel)) > marginDistance:
                negativePaths.append(negativePath)
                negativeLabels.append(int(negativeLabel))
                negativeRelativeIdxs.append(int(negativeRelativeIdx))
                usedNegativeIndexes.append(index)
                n += 1

                # If we have too difficult time to find hard negatives, just find some random negatives.
            if counter > nPositivePaths:
                minDistance = 0
                maxDistance = np.max(allLabels)

    return negativeRelativeIdxs, negativeLabels, negativePaths
