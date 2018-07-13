import numpy as np
import math

def testFunctionThatDoesDoAnyThing():
	return 1

def dumpUsedPanoids(usedPanoids, directory):

    labelFile = open(directory + 'usedPanoids.txt', 'w')

    for usedId in usedPanoids:
        labelFile.write("{}\n".format(usedId))

    labelFile.close()


def dumpCityInfo(uniqueLabelCounter, totalDownloadedSequences, totalDownloadedSequencesKm,
             totalDownloadedSequencesPerLength, directory):

    labelFile = open(directory + 'cityInfo.txt', 'w')

    labelFile.write("{}\n".format(uniqueLabelCounter))
    labelFile.write("{}\n".format(totalDownloadedSequences))
    labelFile.write("{}\n".format(totalDownloadedSequencesKm))

    for sequenceLength in totalDownloadedSequencesPerLength:
        labelFile.write("{}\n".format(sequenceLength))

    labelFile.close()

def getUsedPanoids(directory):

    usedPanoids = []

    labelFile = open(directory + 'usedPanoids.txt', 'r')

    for panoid in labelFile:
        usedPanoids.append(panoid)

    labelFile.close()

    return usedPanoids

def getCityInfo(directory):
    totalDownloadedSequencesPerLength = []

    labelFile = open(directory + 'cityInfo.txt', 'r')

    for i, line in enumerate(labelFile):
        if '\n' in line:
            line = line[:-1]
        if i == 0:
            uniqueLabelCounter = int(line)
        elif i == 1:
            totalDownloadedSequences = int(line)
        elif i == 2:
            totalDownloadedSequencesKm = float(line)
        else:
            totalDownloadedSequencesPerLength.append(round(float(line)))

    labelFile.close()

    return uniqueLabelCounter, totalDownloadedSequences, totalDownloadedSequencesKm, totalDownloadedSequencesPerLength


def measure(lat1, lon1, lat2, lon2):  # generally used geo measurement function
    R = 6378.137  # Radius of earth in KM
    dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
    dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(lat1 * math.pi / 180) * math.cos(
        lat2 * math.pi / 180) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d * 1000  # meters

def closest_node_in_meters(node, nodes):
    nodes = np.asarray(nodes)

    lat1 = node[0]
    lon1 = node[1]

    dist_2 = []

    for existingNode in nodes:
        lat2 = existingNode[0]
        lon2 = existingNode[1]
        dist_2.append(measure(lat1, lon1, lat2, lon2))

    dist_2 = np.array(dist_2)

    return np.argmin(dist_2), np.min(dist_2)



def sortPointsOfInterestByDate(pointsOfInterest,pos):
    gps = {}

    for point in pointsOfInterest:
        year = point['year']
        month = point['month']

        if len(str(month)) == 1:
            month = "0" + str(month)

        if str(year) + str(month) in gps:

            lat = point['lat']
            lon = point['lon']
            panoid = point['panoid']

            # Find orientation of at this point
            index = closest_node([lat, lon], pos[:, 0:2])
            orientation = pos[index, 2]

            dict = gps[str(year) + str(month)]

            if not isinstance(dict['lat'], list):
                lat_list = []
                lon_list = []
                panoid_list = []
                orientation_list = []

                lat_list.append(dict['lat'])
                lon_list.append(dict['lon'])
                panoid_list.append(dict['panoid'])
                orientation_list.append(dict['orientation'])

            else:
                lat_list = dict['lat']
                lon_list = dict['lon']
                panoid_list = dict['panoid']
                orientation_list = dict['orientation']

                lat_list.append(lat)
                lon_list.append(lon)
                panoid_list.append(panoid)
                orientation_list.append(orientation)

            tmp_dict = {'lat': lat_list, 'lon': lon_list, 'panoid': panoid_list, 'orientation': orientation_list}

            gps[str(year) + str(month)] = tmp_dict

        if str(year) + str(month) not in gps:
            lat_list = point['lat']
            lon_list = point['lon']
            panoid_list = point['panoid']

            # Find orientation of at this point
            index = closest_node([lat_list, lon_list], pos[:, 0:2])
            orientation_list = pos[index, 2]

            tmp_dict = {'lat': lat_list, 'lon': lon_list, 'panoid': panoid_list, 'orientation': orientation_list}
            gps[str(year) + str(month)] = tmp_dict

    return gps

def closest_node(node, nodes):
    nodes = np.asarray(nodes)
    dist_2 = np.sum((nodes - node) ** 2, axis=1)
    return np.argmin(dist_2)

def getFromTo(dir):
    start = dir.find("[")
    end1 = dir.find(",")
    num1 = np.float32(dir[start + 1:end1])
    end2 = dir.find("]")
    num2 = np.float32(dir[end1 + 1:end2])
    from_ = [num1, num2]

    tmp = dir[end2 + 1:]

    start = tmp.find("[")
    end1 = tmp.find(",")
    num1 = np.float32(tmp[start + 1:end1])
    end2 = tmp.find("]")
    num2 = np.float32(tmp[end1 + 1:end2])
    to_ = [num1, num2]

    return from_,to_