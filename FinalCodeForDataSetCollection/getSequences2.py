import math
import numpy as np

from  helpers import measure

def getSequences(gps, numFrames = 5, numDates = 4, maxDistanceBetweenPoints = 20, maxDistanceBetweenStartingPoints = 100, usedPanoids = []):

    #Split data such that a sequence is not longer than x meters
    sequenceSplits  = splitData(gps, numFrames,maxDistanceBetweenPoints)

    #Find sets of sequence that are the same place (distance between starting position is less than y meters) but at different time points

    sequences, usedPanoids = findSequencesWithDifferentTimeAndSamePlace(sequenceSplits,numDates,maxDistanceBetweenStartingPoints, usedPanoids, numFrames)

    return sequences, usedPanoids

def findSequencesWithDifferentTimeAndSamePlace(sequenceSplits,numDates, maxDistanceBetweenStartingPoints, usedPanoids, numFrame):
    # For each sequence for all the sequences with different dates
    # and add all the sequence with are close to each other to a list


    finalSequences = []

    for outer in range(len(sequenceSplits)):

        unique = True
        for i in range(len(sequenceSplits[outer])):
            panoidOuter = sequenceSplits[outer][i][3]
            if panoidOuter in usedPanoids:
                unique = False

        if unique:

            yearOfOuter = sequenceSplits[outer][0][0]
            firstLatOuter = sequenceSplits[outer][0][1]
            firstLonOuter = sequenceSplits[outer][0][2]

            tmpUsedPanoids = []

            for i in range(len(sequenceSplits[outer])):
                panoidOuter = sequenceSplits[outer][i][3]

                tmpUsedPanoids.append(panoidOuter)

            tmp = []
            usedYears = []
            usedYears.append(yearOfOuter)
            tmp.append(sequenceSplits[outer])
             # we might as well already append it. Either we look everything through and dont find a matching sequence, and then it doesn't matter if we have it here.

            for inner in range(len(sequenceSplits)):
                yearOfInner = sequenceSplits[inner][0][0]

                # If any of the panoids are already used, we don't want to use the sequence.

                unique = True
                for i in range(len(sequenceSplits[inner])):
                    panoidInner = sequenceSplits[inner][i][3]
                    if panoidInner in usedPanoids:
                        unique = False

                    if panoidInner == "HCB210nwx_o9tMyHJ-rhfQ" and unique != False:
                        stop = True

                # If it is a unique path combination. This condition is necessary to avoid doublicates
                if unique:
                    if numFrame == 20:
                        stop = True
                    # If we have two sequence with different dates
                    if yearOfInner not in usedYears:

                        firstLatInner = sequenceSplits[inner][0][1]
                        firstLonInner = sequenceSplits[inner][0][2]

                        distance = measure(firstLatInner,firstLonInner,firstLatOuter,firstLonOuter)

                        # And the distance between the first observations are smaller than a distance
                        if distance < maxDistanceBetweenStartingPoints:

                            tmp.append(sequenceSplits[inner])
                            usedYears.append(yearOfInner)

                            for i in range(len(sequenceSplits[inner])):
                                panoidInner = sequenceSplits[inner][i][3]

                                tmpUsedPanoids.append(panoidInner)

                            if len(tmp) == (numDates):

                                finalSequences.append(tmp)
                                tmp = []

                                for panoid in tmpUsedPanoids:
                                    usedPanoids.append(panoid)

                                tmpUsedPanoids = []


    return finalSequences, usedPanoids


def splitData(gps, numFrames, maxDistanceBetweenPoints):

    goodSequences = []

    for year in gps:
        lats = gps[year]['lat']
        lons = gps[year]['lon']
        panoids = gps[year]['panoid']
        orientation = gps[year]['orientation']

        tmpSequence = []

        if isinstance(lats,list): # We have to check if there are multiple observations from a given year.

            for i in range(1,len(lats)):

                distanceFromPreviousPoint = measure(lats[i-1],lons[i-1],lats[i],lons[i])

                if distanceFromPreviousPoint < maxDistanceBetweenPoints:

                    # temporally append previous point
                    tmpSequence.append([year,lats[i-1],lons[i-1],panoids[i-1],orientation[i-1]])

                    if len(tmpSequence) == numFrames:

                        # Append the sequence to the acceptable sequences according to split
                        goodSequences.append(tmpSequence)
                        tmpSequence = []

                else: # Since the points are order it will mean that it was not possible to find a sufficiently long sequence. Therefore we reset.

                    tmpSequence = []

    return goodSequences
