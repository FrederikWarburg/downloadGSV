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

    print(cityName)
	
    continueWithCity = True
    plotInterpolationResults = False
    plotPanoidsPositionResults = False
    plotChosenSequences = False
    download = True
    testing = False

    apiKey = 'AIzaSyDXmwm0xlivvdNj2JB2aBMSCCCmD3sSW9g'
    chains = ["mcdonalds", "cinema", "stadium"]

    baseDirectory =  '/home/frederik/Desktop/dataset/{}/'.format(cityName)

    cityCoords = [[19.409084, -99.145136], [42.357978, -71.060782], [33.900527, -118.159436], [40.414523, -3.705759],
                  [51.521473,  -0.105750], [48.852287,   2.346714], [41.399400,    2.181038], [37.879586, -122.270670]]

    if cityName == 'Mexico City':
        cityCoord = cityCoords[0]
    elif cityName == 'Boston':
        cityCoord = cityCoords[1]
    elif cityName == 'Los Angeles':
        cityCoord = cityCoords[2]
    elif cityName == 'Madrid':
        cityCoord = cityCoords[3]
    elif cityName == 'London':
        cityCoord = cityCoords[4]
    elif cityName == 'Paris':
        cityCoord = cityCoords[5]
    elif cityName == 'Barcelona':
        cityCoord = cityCoords[6]
    elif cityName == "San Francisco":
        cityCoord = cityCoords[7]

    lat = cityCoord[0]
    lon = cityCoord[1]

    numFrames = np.array(range(30,4,-1)) # max 50 frames and min 5 frames
    numDates = 4
    maxDistanceBetweenPoints = 20 # m
    maxDistanceBetweenStartingPoints = 30 # m

    # This enables os to continue with the same city eventhough the program is stopped.
    if continueWithCity:
        uniqueLabelCounter, totalDownloadedSequences, totalDownloadedSequencesKm, totalDownloadedSequencesPerLength = getCityInfo(baseDirectory)
        usedPanoids = getUsedPanoids(baseDirectory)

    else:
        uniqueLabelCounter = 0 # Used to label data such that each point in a radius of 15 m gets the same label.
        totalDownloadedSequencesKm = 0  # How many km we have downloaded
        totalDownloadedSequences = 0  # How many sequences we have download
        totalDownloadedSequencesPerLength = np.zeros(len(numFrames))  # How many sequences per length: f.eks 1 sequence of 5 frame, 2 sequence of 6 frames, ...
        usedPanoids = []

    routePoints = generateRoutes(chains,lat,lon,apiKey)
    print(cityName)

    for i, from_ in enumerate(routePoints):
        for j, to_ in enumerate(routePoints):
            if i!=j:
                
                if measure(from_[0],from_[1],to_[0],to_[1]) > 1000: # distance between points must be more than 1 km

                    # This enables os to continue with the same city eventhough the program is stopped.
                    currentFolders = os.listdir(baseDirectory)
                   
                    if 'from: {0} to: {1}'.format(str(from_),str(to_)) not in currentFolders:

                        #t0 = time.time()

                        #print("Downloading street view images from " + str(from_) + " to "+ str(to_))

                        directory = baseDirectory+ 'from: {0} to: {1}/'.format(str(from_),str(to_))

                        os.makedirs(directory)

                        if not testing:
                            lats,lons, pos = getGeoCoordinates(from_,to_, apiKey)

                            labelPos = pos[:, :2]

                            labels = list(range(uniqueLabelCounter, uniqueLabelCounter + len(labelPos)))
                            uniqueLabelCounter += len(labels)
                            #t1 = time.time()
                            #print("We have the geo-coordinates of this route. It took " + str(t1-t0) + " seconds" )

                            if plotInterpolationResults:
                                plt = plotInterpolation(pos, lats, lons, True)
                                plt.show()

                            #######
                            # Note that it takes a long time to get the panoids...
                            ######

                            pointsOfInterest = getPointsOfInterest(pos)

                            #t2 = time.time()
                            #print("We have the points of interest of this route. It took " + str(t2 - t1) + " seconds")

                            ###########
                            # Sort by date
                            ##########

                            gps = sortPointsOfInterestByDate(pointsOfInterest, pos)

                            if plotPanoidsPositionResults:
                                plotPanoidsPosition(gps,pos)

                            #t3 = time.time()
                            #print("We have the sorted the points of this route. It took " + str(t3 - t2) + " seconds")

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

                        #if not testing:
                        #    print("We have gotten the sequences this route. It took " + str(t4 - t3) + " seconds")

                        #############
                        # Download images
                        ##############

                        displayResults(allSequences, download, directory, apiKey, cityCoord, labels, labelPos,cityName)

                        #t5 = time.time()

                        #print("We have the download the images this route. It took " + str(t5 - t4) + " seconds")

                        #print("The total time of this route was " + str(t5 - t0))

                        totalDownloadedSequences += len(allSequences)

                        distance, distancesOfEachSequence, framesOfEachSequence = calculateDistanceOfSequences(allSequences)
                        totalDownloadedSequencesKm += distance

                        print(cityName)
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
    
