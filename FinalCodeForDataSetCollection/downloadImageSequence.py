import google_streetview.api
import google_streetview.helpers
import json
import cv2
from gmplot import gmplot
import math
import imageio
from helpers import closest_node_in_meters
import numpy as np
import os
import pandas as pd
import time

from pathEstimation import bspline_planning
from getSequences2 import measure
import matplotlib.pyplot as plt

def displayResults(sequences,download, directory, apiKey, center, labels, labelPos, cityName):
    dict = {}

    for s, sequence in enumerate(sequences):
        print(str(s) + " / " + str(len(sequences)))
        tmp_date = {}

        sequenceDirectory = directory + "sequenceSet" + str(s)
        os.makedirs(sequenceDirectory)

        datesToWriteToFile = []

        for year in sequence:
            tmp_dict = {}

            datesToWriteToFile.append(year[0][0])

            dateDirectory = sequenceDirectory + "/" + str(year[0][0])
            os.makedirs(dateDirectory)

            reverseDateDirectory = sequenceDirectory + "/Reverse" + str(year[0][0])
            os.makedirs(reverseDateDirectory)

            for frame, obs in enumerate(year):

                date = obs[0]
                lat = obs[1]
                lon = obs[2]
                panoid = obs[3]
                orientation = (obs[4] * 180/math.pi)%360

                if download:
                    filename = dateDirectory + "/{}.png".format(frame)
                    downloadImage(panoid, orientation, filename, apiKey, cityName)

                    filename = reverseDateDirectory + "/{}.png".format(frame)
                    downloadImage(panoid, (orientation+180)%360, filename, apiKey, cityName)

                if tmp_dict == {}:

                    pre_panoid = []
                    pre_lat = []
                    pre_lon = []
                    pre_orientation = []
                    pre_name = []

                    pre_panoid.append(panoid)
                    pre_lat.append(lat)
                    pre_lon.append(lon)
                    pre_orientation.append(orientation)
                    pre_name.append("{}.png".format(frame))

                    tmp_dict = {'panoid': pre_panoid, 'lat': pre_lat, 'lon':pre_lon, 'orientation':pre_orientation, 'name': pre_name}
                else:
                    pre_panoid = tmp_dict['panoid']
                    pre_lat = tmp_dict['lat']
                    pre_lon = tmp_dict['lon']
                    pre_orientation = tmp_dict['orientation']
                    pre_name = tmp_dict['name']

                    pre_panoid.append(panoid)
                    pre_lat.append(lat)
                    pre_lon.append(lon)
                    pre_orientation.append(orientation)
                    pre_name.append("{}.png".format(frame))

                    tmp_dict = {'panoid': pre_panoid, 'lat': pre_lat, 'lon':pre_lon, 'orientation':pre_orientation, 'name': pre_name}

            tmp_date[str(date)] = tmp_dict

        # Assaign labels
        df = makeLabelFile(datesToWriteToFile,tmp_date, labels, labelPos)

        # create sequenceInformationFile
        df.to_csv(sequenceDirectory + "/info.csv",header=['year','panoid','imageName','latitude','longitude','placeID'],index=False)

        # create date file
        file = open(sequenceDirectory + "/dates.txt", 'w')
        for dateToWriteToFile in datesToWriteToFile:
            file.write(str(dateToWriteToFile) + '\n')

        file.close()

        # Append to
        dict[str(s)] = tmp_date

    # Dump result to json file
    with open(directory + 'overview.json', 'w') as fp:
        json.dump(dict, fp, indent=4, sort_keys=True)

    # make plot of the results
    gmap = makePlotOfResults(dict,center[0],center[1])
    gmap.draw(directory + "overview_map.html")


def makeLabelFile(datesToWriteToFile, sequenceSet, labels, labelPos):
    # Frame labels

    allLabels = []  # Each point will get an label
    allNames = []
    allIDs = []
    allDates = []
    allLats = []
    allLons = []

    # uniqueLabelCounter = 0 This is assigned as argument such that labels will be unique across sequencesSets

    lat = []
    lon = []
    name =[]
    panoid = []

    # Not a very nice way of doing the work - but it gets the work done. Reallocate the sequence to 1 arrays instead of 4
    for i, sequenceLabels in enumerate(sequenceSet):
        sequence = sequenceSet[sequenceLabels]

        latTmp = sequence['lat']
        lonTmp = sequence['lon']
        nameTmp = sequence['name']
        panoidTmp = sequence['panoid']

        for j in range(len(latTmp)):
            lat.append(latTmp[j])
            lon.append(lonTmp[j])
            name.append(nameTmp[j])
            panoid.append(panoidTmp[j])

            allDates.append(datesToWriteToFile[i])

    for j in range(len(lat)):

        # Calculate labels
        position = [lat[j], lon[j]]
        idx, dist = closest_node_in_meters(position, labelPos)
        label = labels[idx]
        allLabels.append(label)

        allLats.append(lat[j])
        allLons.append(lon[j])
        allNames.append(name[j])
        allIDs.append(panoid[j])

    matrix = np.array([allDates, allIDs, allNames, allLats, allLons, allLabels])
    df = pd.DataFrame(np.transpose(matrix))

    return df


def makePlotOfResults(data, lat, lon):

    gmap = gmplot.GoogleMapPlotter(lat,lon, 12)

    colors = ['#f44283','#f44283','#f44283','#5b91a0','#632596','#963725','#d6b753', '#20b2aa','#ffc3a0','#fff68f','#f6546a',
            '#468499','#ff6666','#666666','#66cdaa','#c39797','#00ced1','#ff00ff','#008000','#088da5']
    colors2 = ['red','green','blue','yellow']

    for j, s in enumerate(data):
        dates = data[s]
        for i, date in enumerate(dates):
            obs = dates[date]

            lats = obs['lat']
            lons = obs['lon']

            gmap.scatter(lats, lons, colors2[i%len(colors2)], edge_width=10)
            gmap.plot(lats, lons, colors[j%len(colors)], edge_width=10)

    return gmap


def downloadImage(panoid, heading, filename, apiKey, cityName):

    tmpStorage = "{}TmpStorage".format(cityName)

    prevImage = cv2.imread(tmpStorage + "/gsv_0.jpg")

    # Create a dictionary with multiple parameters separated by ;
    apiargs = {
      'pano': panoid,
      'size': '640x640',
      'heading': str(heading),
      'fov': '90',
      'pitch': '0',
      'key': apiKey
    }

    # Get a list of all possible queries from multiple parameters
    api_list = google_streetview.helpers.api_list(apiargs)

    # Create a results object for all possible queries
    results = google_streetview.api.results(api_list)

    # Download images to directory 'downloads'
    results.download_links(tmpStorage)

    newImage = cv2.imread(tmpStorage + "/gsv_0.jpg")

    if not np.all(newImage == prevImage):  # I dont trust the meta object. We look at the image directly.
        removeGoogleLogo(filename, cityName)
    else:
        print("The current image is the same as the previous image. This is properly because we exceeded the amount of downloads per day. It is decided to pause the program for 19h")
        time.sleep(19*60*60)
        downloadImage(panoid,heading,filename,apiKey,cityName)


def removeGoogleLogo(filename, cityName):

    try:

        im = cv2.cvtColor(cv2.imread("{}TmpStorage/gsv_0.jpg".format(cityName)),cv2.COLOR_BGR2RGB)
        im = im[:-40,:,:]

        imageio.imwrite(filename,im)

    except:
        print("We encountered an error when reading image: " + filename)
