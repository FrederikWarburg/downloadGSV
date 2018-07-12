
import math
import numpy as np


def calculateOrientation(directions):
    # Inspired by
    # https://math.stackexchange.com/questions/529555/signed-angle-between-2-vectors


    #directions = np.array(directions)
    #u = np.array(directions[0, :])

    north = np.array([1,0])
    u = north

    angles = []
    for direction in directions:
        #angle = np.arccos(np.matmul(startDirection, direction))  # nominator always 1 because of previous normalization

        v = np.array(direction)

        result = math.atan2(v[1],v[0])-math.atan2(u[1],u[0])

        if result > math.pi:
            result = result - 2*math.pi
        else:
            result = result + 2*math.pi

        angles.append(result)

    return angles

def getOrientations(lats, lons):
    lats_new = []
    lons_new = []
    directions = []

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
    orientations = calculateOrientation(directions)
    pos = np.transpose(np.array([lats_new, lons_new,orientations]))

    return pos


def getOrientations2(lats, lons):

    # Define global direction vector pointing towards north

    north = (1,0)
    deltaLat = lats[1:] - lats[:-1]
    deltaLon = lons[1:] - lons[:-1]
    # vector from A to B will always point towards north.
    orientations = []
    for i in range(len(deltaLat)):

        orientation = calculate_initial_compass_bearing((deltaLat[i],deltaLon[i]), north)

        orientations.append(orientation)

    pos = np.transpose(np.array([lats[:-1],lons[:-1],orientations]))
    print(pos)
    return pos


def calculate_initial_compass_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    #compass_bearing = math.radians(compass_bearing) # change later
    return compass_bearing



pos = np.array([[ 5.15012500e+01, -1.19840000e-01],
 [ 5.15013076e+01, -1.19830078e-01],
 [ 5.15013646e+01, -1.19820070e-01]])

import matplotlib.pyplot as plt

#plt.plot(pos[:,0],pos[:,1],'o-')


northS = [5.15012500e+01 + 0.0001,-1.19840000e-01]
east = [5.15012500e+01,-1.19840000e-01 + 0.0001]
vest = [5.15012500e+01,-1.19840000e-01 - 0.0001]

north1 = (5.15012500e+01 + 0.0001,-1.19840000e-01)


#plt.plot(northS[0],northS[1],'go')
#plt.plot(east[0],east[1],'ro')
#plt.plot(vest[0],vest[1],'co')

plt.axis('equal')

plt.plot(0,0,'ro')
plt.plot(0,1,'bo')
plt.plot(1,0,'go')
plt.plot(0,-1,'co')
plt.plot(-1,0,'yo')



plt.show()

for i in range(len(pos)):
    point = (pos[i,0],pos[i,0])
    ori = calculate_initial_compass_bearing(point,north1)
    print(ori)