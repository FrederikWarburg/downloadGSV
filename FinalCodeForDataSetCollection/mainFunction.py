from pathEstimation import getGeoCoordinates
from visualization import plotInterpolation, plotPanoidsPosition, calculateDistanceOfSequences, getYearsOfSequenceSet
from googleStreetViewAPIcalls import getPointsOfInterest
from helpers import sortPointsOfInterestByDate, getCityInfo, getUsedPanoids, dumpUsedPanoids, dumpCityInfo, measure
from getSequences2 import getSequences
from generateRoutes2 import generateRoutes
from downloadImageSequence import displayResults
#from testing import getGPS

import json
import os
import time
import numpy as np

def mainFunction(cityName):

    continueWithCity = False
    print(cityName)
    plotInterpolationResults = False
    plotPanoidsPositionResults = False
    plotChosenSequences = False
    download = True
    testing = False

    apiKey = 'AIzaSyDXmwm0xlivvdNj2JB2aBMSCCCmD3sSW9g'
    chains = ["mcdonalds", "cinema", "stadium"]

    baseDirectory =  '/Users/frederikwarburg/Desktop/Zaragoza/dataset2/{}/'.format(cityName)

    cityCoords = [[51.507351, -0.127758], [42.357978, -71.060782], [33.900527, -118.159436], [40.414523, -3.705759]]

    if cityName == 'London':
        cityCoord = cityCoords[0]
    elif cityName == 'Boston':
        cityCoord = cityCoords[1]
    elif cityName == 'Los Angeles':
        cityCoord = cityCoords[2]
    elif cityName == 'Madrid':
        cityCoord = cityCoords[3]

    lat = cityCoord[0]
    lon = cityCoord[1]



    numFrames = np.array(range(30,4,-1)) # max 50 frames and min 5 frames
    numDates = 4
    maxDistanceBetweenPoints = 20 # m
    maxDistanceBetweenStartingPoints = 30 # m

    # This enables os to continue with the same city eventhough the program is stopped.
    if continueWithCity:
        uniqueLabelCounter, totalDownloadedSequences, totalDownloadedSequencesKm, totalDownloadedSequencesPerLength = getCityInfo()
        usedPanoids = getUsedPanoids()

    else:
        uniqueLabelCounter = 0 # Used to label data such that each point in a radius of 15 m gets the same label.
        totalDownloadedSequencesKm = 0  # How many km we have downloaded
        totalDownloadedSequences = 0  # How many sequences we have download
        totalDownloadedSequencesPerLength = np.zeros(len(numFrames))  # How many sequences per length: f.eks 1 sequence of 5 frame, 2 sequence of 6 frames, ...
        usedPanoids = []

    routePoints = [[51.5176, -0.08237], [51.50282, -0.11136], [51.51017, -0.1307], [51.50124, -0.11969], [51.51361, -0.12907], [51.50121, -0.19307], [51.49826, -0.16571], [51.50631, -0.12693], [51.51346, -0.15936], [51.52436, -0.13799], [51.51375, -0.14962], [51.51365, -0.12913], [51.51099, -0.1339], [51.51795, -0.11074], [51.50885, -0.1245], [51.51434, -0.10778], [51.51786, -0.11968], [51.53011, -0.12317], [51.51619, -0.17472], [51.48439, -0.06841], [51.50897, -0.13432], [51.49606, -0.04483], [51.51086, -0.13039], [51.51984, -0.09298], [51.52115, -0.05112], [51.5243, -0.07399], [51.51148, -0.13032], [51.51126, -0.12939], [51.4987, -0.09859], [51.46122, -0.11501], [51.50783, -0.02249], [51.47448, -0.02448], [51.51067, -0.13374], [51.50616, -0.01805], [51.46251, -0.13819], [51.50483, -0.11366], [51.50872, -0.13236], [51.45642, -0.07617], [51.52358, -0.07208], [51.51263, -0.13062], [51.55488, -0.10843], [51.48141, -0.19139], [51.48166, -0.19095], [51.53049, -0.17103], [51.55509, -0.10928], [51.55157, -0.11379], [51.48261, -0.19155]]


    for i, from_ in enumerate(routePoints):
        for j, to_ in enumerate(routePoints):
            if i!=j:
                print(i,j, measure(from_[0],from_[1],to_[0],to_[1]))
                if measure(from_[0],from_[1],to_[0],to_[1]) > 1000: # distance between points must be more than 1 km

                    # This enables os to continue with the same city eventhough the program is stopped.
                    currentFolders = os.listdir(baseDirectory)
                    print(currentFolders)
                    if 'from: {0} to: {1}'.format(str(from_),str(to_)) not in currentFolders:

                        #t0 = time.time()

                        print("Downloading street view images from " + str(from_) + " to "+ str(to_))

                        directory = baseDirectory+ 'from: {0} to: {1}/'.format(str(from_),str(to_))

                        os.makedirs(directory)

                        if not testing:
                            lats,lons, pos = getGeoCoordinates(from_,to_, apiKey)
                            print(lats, lons)
                            #t1 = time.time()
                            print("We have the geo-coordinates of this route. It took " + str(t1-t0) + " seconds" )

                            if plotInterpolationResults:
                                plt = plotInterpolation(pos, lats, lons, True)
                                plt.show()

                            #######
                            # Note that it takes a long time to get the panoids...
                            ######

                            pointsOfInterest = getPointsOfInterest(pos)

                            #t2 = time.time()
                            print("We have the points of interest of this route. It took " + str(t2 - t1) + " seconds")

                            ###########
                            # Sort by date
                            ##########

                            gps = sortPointsOfInterestByDate(pointsOfInterest, pos)

                            if plotPanoidsPositionResults:
                                plotPanoidsPosition(gps,pos)

                            #t3 = time.time()
                            print("We have the sorted the points of this route. It took " + str(t3 - t2) + " seconds")

                        # For testing and debugging
                        #else:
                        #    gps = getGPS()

                        allSequences = []

                        for i, numFrame in enumerate(numFrames):
                            #########
                            # Get sequences
                            #########

                            sequences, usedPanoids = getSequences(gps,numFrame,numDates,maxDistanceBetweenPoints,maxDistanceBetweenStartingPoints, usedPanoids)

                            totalDownloadedSequencesPerLength[i] = totalDownloadedSequencesPerLength[i] + len(sequences)

                            for sequence in sequences:
                                allSequences.append(sequence)

                        #t4 = time.time()

                        if not testing:
                            print("We have gotten the sequences this route. It took " + str(t4 - t3) + " seconds")

                        #############
                        # Download images
                        ##############

                        uniqueLabelCounter = displayResults(allSequences,download,directory, apiKey, city, uniqueLabelCounter)

                        #t5 = time.time()

                        print("We have the download the images this route. It took " + str(t5 - t4) + " seconds")

                        print("The total time of this route was " + str(t5 - t0))

                        totalDownloadedSequences += len(allSequences)

                        distance, distancesOfEachSequence, framesOfEachSequence = calculateDistanceOfSequences(allSequences)
                        totalDownloadedSequencesKm += distance

                        print("We have now downloaded at total of " + str(totalDownloadedSequences) + " sequences!")
                        print("We have now downloaded at total of " + str(totalDownloadedSequencesKm) + " km of sequences!")

                        for i, index in enumerate(totalDownloadedSequencesPerLength):
                            print("There are " + str(index) + " sequences of " + str((len(totalDownloadedSequencesPerLength)-i) + 4) + " frames")

                        print()

                        dumpUsedPanoids(usedPanoids, baseDirectory)
                        dumpCityInfo(uniqueLabelCounter, totalDownloadedSequences, totalDownloadedSequencesKm, totalDownloadedSequencesPerLength, baseDirectory)

                        # Create summary file from path

                        summaryArray = {}

                        summaryArray['name'] = 'from: {0} to: {1}'.format(str(from_),str(to_))
                        summaryArray['numberOfSequenceSets'] = len(allSequences)
                        summaryArray['totalKm'] = distance

                        sequenceDetails = {}

                        for idx, sequenceSet in enumerate(allSequences):
                            dates = getYearsOfSequenceSet(directory + 'sequenceSet{}/dates.txt'.format(idx))

                            context = {}

                            context['frames'] = framesOfEachSequence[idx]
                            context['km'] = distancesOfEachSequence[idx]
                            context['dates'] = dates

                            sequenceDetails["sequence{}".format(idx)] = context

                        summaryArray['sequenceSets'] = sequenceDetails

                        # Dump result to json file
                        with open(directory + '/description.json', 'w') as fp:
                            json.dump(summaryArray, fp, indent=4)
    
