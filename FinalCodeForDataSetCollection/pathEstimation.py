import numpy as np
import math
import polyline
import googlemaps
import scipy.interpolate as si


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
    #positions = getOrientations(int_lats,int_lons)
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
        #angle = np.arccos(np.matmul(startDirection, direction))  # nominator always 1 because of previous normalization

        v = np.array(direction)

        result = math.atan2(v[1],v[0])-math.atan2(u[1],u[0])

        if result > math.pi:
            result = result - 2*math.pi
        else:
            result = result + 2*math.pi

        angles.append(result % (2*math.pi))

    return angles

def getOrientations(lats, lons):
    lats_new = []
    lons_new = []
    directions = []

    # First calculate the oritentation relative to world coordinates
    north_dx = math.cos(lons[0])
    north_dy = math.sin(lons[0])

    north = np.array([north_dx, north_dy])

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
    print(pos)
    return pos


def getOrientations2(lats, lons):

    # Define global direction vector pointing towards north

    north = (1,0)
    deltaLat = lats[1:] - lats[:-1]
    deltaLon = lons[1:] - lons[:-1]
    # vector from A to B will always point towards north.
    orientations = []
    for i in range(len(deltaLat)-1):

        orientation = calculate_initial_compass_bearing((deltaLat[i],deltaLon[i]), (deltaLat[i+1],deltaLon[i+1]))

        orientations.append(orientation)

    pos = np.transpose(np.array([lats[:-2],lons[:-2],orientations]))


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
    compass_bearing = math.radians(compass_bearing) # change later
    return compass_bearing
