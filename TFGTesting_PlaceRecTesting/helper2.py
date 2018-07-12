import os
import pandas as pd
import numpy as np
import cv2

def loadImages(dirs, city, inp, ref):
    imInput, labelInput, datesInput = [], [], []
    imRefs, labelRefs, datesRefs = [], [], []

    for dir in dirs:
        if dir != ".DS_Store" and dir != "cityInfo.txt" and dir != "usedPanoids.txt":

            path = city + "/" + dir

            tmpImInput, tmpLabelInput, tmpDatesInput = getImagesAndLabels(path, inp)
            tmpImRef, tmpLabelRef, tmpDatesRef = getImagesAndLabels(path, ref)

            for i in range(len(tmpLabelInput)):
                imInput.append(tmpImInput[i])
                labelInput.append(tmpLabelInput[i])
                datesInput.append(tmpDatesInput[i])

                imRefs.append(tmpImRef[i])
                labelRefs.append(tmpLabelRef[i])
                datesRefs.append(tmpDatesRef[i])

    return imInput, labelInput, datesInput, imRefs, labelRefs, datesRefs



def getImagesAndLabels(dir, ref):

    allDates = []
    allImages = []
    allLabels = []

    for file in os.listdir(dir):
        if file != "description.json" and file!="overview_map.html" and file!= "overview.json" and file!=".DS_Store":

            dates = getDates(dir + "/" + file)

            date = dates[ref]

            images = getImages(dir + "/" + file + "/" + date)
            labels = getLabels(dir + "/" + file, date)

            for image,label in zip(images,labels):

                allImages.append(image)
                allLabels.append(label)
                allDates.append(date)

    return allImages, allLabels, allDates


def getClosestReferenceLabels(input_labels, reference_labels):

    trueLabels = []
    reference_labels  = np.array(reference_labels)
    for inputLabel in input_labels:

        diff = abs(inputLabel - reference_labels)
        idx = np.argmin(diff)
        trueLabels.append(reference_labels[idx])

    return trueLabels

def getImages(path):

    images = []

    numberOfImages = len(os.listdir(path))

    for imagePath in range(numberOfImages):

        im = cv2.imread(path + "/" + str(imagePath) + ".png")
        im = cv2.resize(im, (224, 224), interpolation=cv2.INTER_AREA)
        im = cv2.cvtColor(im,cv2.COLOR_BGR2RGB)

        images.append(im)

    return images


def getDates(path):

    dates = []

    file = open(path + "/dates.txt")

    for line in file:
        dates.append(line[:-1])

    dates = np.sort(np.array(dates))

    return dates

def getLabels(path, date):

	data = pd.read_csv(path + '/info.csv', header=0)
	data = np.array(data)

	data = data[data[:,0] == int(date),:]

	labels = data[:,-1]

	return labels

def getImageByLabel(imRefs, labelRefs, labels, dates):

    orderedDates = []
    images = []

    for label in labels:

        idx = labelRefs.index(label)
        images.append(imRefs[idx])
        orderedDates.append(dates[idx])

    return images, orderedDates