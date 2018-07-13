import numpy as np
import math
import polyline
import googlemaps
import scipy.interpolate as si
import pandas as pd

def getGeoCoordinates(from_, to_,apiKey):

    # Open Google Maps with API Key
    gmaps = googlemaps.Client(key=apiKey)

    # Request directions via car
    directions_result = gmaps.directions(from_, to_, mode="walking") # mode = driving

    # Get geo coordinates from directions
    lats, lons, distance = getGeoCoord(directions_result)

    # Interpolate path with bspline
    int_lats, int_lons = bspline_planning(np.array(lats),np.array(lons),sn = distance, N = 5) # sn = distance => 1 meter per step

    # Calculates directions
    positions = getOrientations(int_lats,int_lons)

    return lats,lons, positions

def bspline_planning(x, y, sn, N):
    t = range(len(x))
    x_tup = si.splrep(t, x, k=N)
    y_tup = si.splrep(t, y, k=N)

    x_list = list(x_tup)
    xl = x.tolist()
    x_list[1] = xl + [0.0, 0.0, 0.0, 0.0]

    y_list = list(y_tup)
    yl = y.tolist()
    y_list[1] = yl + [0.0, 0.0, 0.0, 0.0]

    ipl_t = np.linspace(0.0, len(x) - 1, sn)
    rx = si.splev(ipl_t, x_list)
    ry = si.splev(ipl_t, y_list)

    return rx, ry

def getGeoCoord(directions_result):

    listOfLines = []
    distance = 0

    steps = directions_result[0]['legs'][0]['steps']

    for i, step in enumerate(steps):
        listOfEncodings = step['polyline']['points']
        listOfLines.append(polyline.decode(listOfEncodings))
        distance += step['distance']['value']

    entirePath = sum(listOfLines, [])

    # Polygon
    lats, lons = zip(*entirePath)

    return lats, lons, distance

def calculateOrientation(directions, north):
    # Inspired by
    # https://math.stackexchange.com/questions/529555/signed-angle-between-2-vectors

    u = north

    angles = []
    for direction in directions:

        v = np.array(direction)

        result = math.atan2(v[1],v[0])-math.atan2(u[1],u[0])

        angles.append(result % (2*math.pi))

    return angles

def getOrientations(lats, lons):
    lats_new = []
    lons_new = []
    directions = []

    # First calculate the oritentation relative to world coordinates
    north = np.array([1,0])

    for i in range(len(lons) - 1):
        dx = lats[i + 1] - lats[i]
        dy = lons[i + 1] - lons[i]

        direction = np.array([dx, dy])

        norminator = np.linalg.norm(direction)

        if np.linalg.norm(direction) != 0.0:
            direction = direction / norminator

            directions.append(direction)
            lats_new.append(lats[i])
            lons_new.append(lons[i])

    directions = np.array(directions)
    orientations = calculateOrientation(directions, north)

    pos = np.transpose(np.array([lats_new, lons_new,orientations]))

    return pos


