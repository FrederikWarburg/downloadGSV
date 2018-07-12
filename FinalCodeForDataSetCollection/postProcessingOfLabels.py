import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathEstimation import bspline_planning
from generateRoutes2 import measure
from helpers import closest_node_in_meters
import re

from pathEstimation import getGeoCoordinates
from helpers import  closest_node_in_meters, getFromTo
apiKey = 'AIzaSyDXmwm0xlivvdNj2JB2aBMSCCCmD3sSW9g'
city = "LondonNewStructure"



def changeLabels(city):

    basePath = '/Users/frederikwarburg/Desktop/Zaragoza/dataset/' + city + "/"

    dirs = os.listdir(basePath) # List of routes: From a to b

    uniqueLabelsCounter = 0

    for dir in dirs:

        if dir != "cityInfo.txt" and dir != "usedPanoids.txt" and dir!= ".DS_Store":

            from_, to_ = getFromTo(dir)

            print(from_,to_)

            lats, lons, pos = getGeoCoordinates(from_, to_, apiKey)
            pos = pos[:,:2]

            labels = list(range(uniqueLabelsCounter, uniqueLabelsCounter + len(pos)))
            uniqueLabelsCounter += len(labels)

            sequenceSetPath = basePath + dir + "/"
            sequencesDirs = os.listdir(sequenceSetPath) # list of sequenceSets

            if ".DS_Store" in sequencesDirs:
                skip = 4
            else:
                skip = 3

            for idx in range(len(sequencesDirs) - skip):

                newLabels = []

                pathToInfo = sequenceSetPath + "sequenceSet" + str(idx) + "/info.csv"

                data = pd.read_csv(pathToInfo)

                lats = np.array(data['latitude'])
                lons = np.array(data['longitude'])

                positions = np.array([lats,lons]).T

                for position in positions:

                    idx, dist = closest_node_in_meters(position,pos)

                    label = labels[idx]

                    newLabels.append(label)
                #year,panoid,imageName,latitude,longitude,placeID

                newdata = pd.DataFrame()

                newdata['year'] = data['year']
                newdata['panoid'] = data['panoid']
                newdata['imageName'] = data['imageName']
                newdata['latitude'] = data['latitude']
                newdata['longitude'] = data['longitude']

                newdata['placeID'] = newLabels

                newdata.to_csv(pathToInfo,index=False)


def getDatesFromCity(city):
    basePath = '/Users/frederikwarburg/Desktop/Zaragoza/dataset/' + city + "/"

    dirs = os.listdir(basePath)  # List of routes: From a to b

    allDatesFromCityDividedByRoute = []
    allDatesFromCity = []


    for dir in dirs:

        allDatesFromRoute = []

        if dir != "cityInfo.txt" and dir != "usedPanoids.txt" and dir!=".DS_Store":
            sequenceSetPath = basePath + dir + "/"
            sequencesDirs = os.listdir(sequenceSetPath)  # list of sequenceSets

            for idx in range(len(sequencesDirs) - 3):

                pathToInfo = sequenceSetPath + "sequenceSet" + str(idx) + "/dates.txt"

                file = open(pathToInfo)

                dates = []

                for line in file:
                    dates.append(line[:-1])

                file.close()

                allDatesFromRoute.append(dates)
                allDatesFromCity.append(dates)

            allDatesFromCityDividedByRoute.append(allDatesFromRoute)

    return allDatesFromCity


def distributionPerYear(dateMatrix):

    # 2000, 2018
    years = np.zeros(18)

    for row in dateMatrix:
        for obs in row:

            year = int(obs[:4]) - 2000

            years[year] += 1

    return years

def distributionPerMonth(dateMatrix):

    # Jan: 0, Dec: 11
    months = np.zeros(12)
    monthsNames = ['Jan','Feb','Mar','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    for row in dateMatrix:
        for obs in row:

            if len(obs) == 5:
                month = int(obs[-1:])

            elif len(obs) == 6:
                month = int(obs[-2:])

            months[month] += 1

    return months, monthsNames

"""
dates = getDatesFromCity(city)
perMonth,monthsNames = distributionPerMonth(dates)
perYear = distributionPerYear(dates)
print(perMonth)
print(monthsNames)

print(perYear)

"""

changeLabels('London')