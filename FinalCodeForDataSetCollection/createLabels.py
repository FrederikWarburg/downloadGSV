import json
import numpy as np
import matplotlib.pyplot as plt
from helpers import measure
import pandas as pd
from_ =[51.52138, -0.15691]
to_ =[51.50631, -0.12693]

directory = "/Users/frederikwarburg/Desktop/Zaragoza/dataset/London11/from: {0} to: {1}/".format(str(from_), str(to_))

with open(directory + 'imageInformation.json', 'r') as fp:
    data = json.load(fp)

# Sequence labels
print(data)

def makeLabelFile(datesToWriteToFile, sequenceSet, uniqueLabelCounter):
    # Frame labels

    allLabels = []  # Each point will get an label
    allPositions = []
    allNames = []
    allIDs = []
    allDates = []

    uniqueLabels = []  # This is a list of all unique labels
    uniquePositions = []

    # uniqueLabelCounter = 0 This is assigned as argument such that labels will be unique across sequencesSets

    for i, sequenceLabels in enumerate(sequenceSet):
        sequence = sequenceSet[sequenceLabels]

        lat = sequence['lat']
        lon = sequence['lon']
        name = sequence['name']
        panoid = sequence['panoid']

        # For every point, check if there is a point in this position already
        for j in range(len(lat)):

            currentPosition = [lat[j], lon[j]]
            currentName = name[j]
            currentPanoid = panoid[j]

            # This is only for the very first labelled observation
            if len(uniquePositions) == 0:

                uniquePositions.append(currentPosition)
                uniqueLabels.append(uniqueLabelCounter)

                allLabels.append(uniqueLabelCounter)
                allPositions.append(currentPosition)
                allNames.append(currentName)
                allIDs.append(currentPanoid)
                allDates.append(datesToWriteToFile[i])

                uniqueLabelCounter += 1

            # For every point except the first one.
            else:

                # find the closest
                idx, val = closest_node_in_meters(currentPosition, uniquePositions)

                # Its the same place and should have same labels
                if val < 5:  # m

                    label = uniqueLabels[idx]

                    allLabels.append(label)
                    allPositions.append(currentPosition)
                    allNames.append(currentName)
                    allIDs.append(currentPanoid)
                    allDates.append(datesToWriteToFile[i])

                # We have a new place and need a new label
                else:
                    uniquePositions.append(currentPosition)
                    uniqueLabels.append(uniqueLabelCounter)

                    allLabels.append(uniqueLabelCounter)
                    allPositions.append(currentPosition)
                    allNames.append(currentName)
                    allIDs.append(currentPanoid)
                    allDates.append(datesToWriteToFile[i])

                    uniqueLabelCounter += 1

    allPositions = np.array(allPositions)

    allLats = allPositions[:, 0]
    allLons = allPositions[:, 1]

    matrix = np.array([allDates, allIDs, allNames, allLats, allLons, allLabels])
    df = pd.DataFrame(np.transpose(matrix))

    return df, uniqueLabelCounter


def makeLabelFile(sequenceSet, uniqueLabelCounter):

    # Frame labels

    allLabels = [] # Each point will get an label
    allPositions = []
    allNames = []
    allIDs =[]
    allSeqLabels = []

    uniqueLabels = [] # This is a list of all unique labels
    uniquePositions = []

    # uniqueLabelCounter = 0 This is assigned as argument such that labels will be unique across sequencesSets

    for i, sequenceLabels in enumerate(sequenceSet):
        sequence = sequenceSet[sequenceLabels]

        lat = sequence['lat']
        lon = sequence['lon']
        name = sequence['name']
        panoid = sequence['panoid']

        # For every point, check if there is a point in this position already
        for j in range(len(lat)):

            currentPosition = [lat[j], lon[j]]
            currentName = name[j]
            currentPanoid = panoid[j]

            # This is only for the very first labelled observation
            if len(uniquePositions) == 0:

                uniquePositions.append(currentPosition )
                uniqueLabels.append(uniqueLabelCounter)

                allLabels.append(uniqueLabelCounter)
                allPositions.append(currentPosition )
                allNames.append(currentName)
                allIDs.append(currentPanoid)
                allSeqLabels.append(sequenceSetLabels)

                uniqueLabelCounter += 1

            # For every point except the first one.
            else:

                # find the closest
                idx, val = closest_node_in_meters(currentPosition, uniquePositions)

                # Its the same place and should have same labels
                if val < 15:  # m

                    label = uniqueLabels[idx]

                    allLabels.append(label)
                    allPositions.append(currentPosition)
                    allNames.append(currentName)
                    allIDs.append(currentPanoid)
                    allSeqLabels.append(sequenceSetLabels)

                # We have a new place and need a new label
                else:
                    uniquePositions.append(currentPosition )
                    uniqueLabels.append(uniqueLabelCounter)

                    allLabels.append(uniqueLabelCounter)
                    allPositions.append(currentPosition)
                    allNames.append(currentName)
                    allIDs.append(currentPanoid)
                    allSeqLabels.append(sequenceSetLabels)

                    uniqueLabelCounter += 1

    allPositions = np.array(allPositions)

    allLats = allPositions[:,0]
    allLons = allPositions[:,1]

    df = pd.DataFrame([allIDs, allNames, allLats, allLons, allSeqLabels, allLabels])

    return df, uniqueLabelCounter

def closest_node_in_meters(node, nodes):
    nodes = np.asarray(nodes)

    lat1 = node[0]
    lon1 = node[1]

    dist_2 = []

    for existingNode in nodes:
        lat2 = existingNode[0]
        lon2 = existingNode[1]
        dist_2.append(measure(lat1,lon1,lat2,lon2))

    dist_2 = np.array(dist_2)

    return np.argmin(dist_2), np.min(dist_2)

# Frame labels

labels = []
tmpPos = []
uniqueLabels = []
positions = []
uniqueLabelCounter = 0
sum = 0
for sequenceSetLabels in data:
    sequenceSet = data[sequenceSetLabels]

    for i, sequenceLabels in enumerate(sequenceSet):
        sequence = sequenceSet[sequenceLabels]

        lat= sequence['lat']
        lon= sequence['lon']
        panoid = sequence['panoid']
        sum += (len(lat))
        plt.plot(lat,lon,'o')

        # For every point, check if there is a point in this position already
        for j in range(len(lat)):

            position = [lat[j],lon[j]]

            if len(positions) == 0:
                positions.append(position)

                uniqueLabels.append(uniqueLabelCounter)

                labels.append(uniqueLabelCounter)
                tmpPos.append(position)

                uniqueLabelCounter += 1

            else:
                # find the closest
                idx, val = closest_node_in_meters(position, positions)

                # Its the same place and should have same labels
                if val < 15: # m

                    label = uniqueLabels[idx]

                    labels.append(label)

                    tmpPos.append(position)

                # We have a new place and need a new label
                else:
                    positions.append(position)

                    uniqueLabels.append(uniqueLabelCounter)

                    labels.append(uniqueLabelCounter)
                    tmpPos.append(position)

                    uniqueLabelCounter += 1


plt.axis('equal')
plt.show()
labels = np.array(labels)
print(np.shape(labels))
print(np.shape(tmpPos))

colors = ['#f44283','#f44283','#f44283','#5b91a0','#632596','#963725','#d6b753', '#20b2aa','#ffc3a0','#fff68f','#f6546a',
        '#468499','#ff6666','#666666','#66cdaa','#c39797','#00ced1','#ff00ff','#008000','#088da5']

for i,pos in enumerate(tmpPos):

    label = labels[i]

    plt.plot(pos[0],pos[1], 'o', color=colors[label%len(colors)])
plt.axis('equal')
plt.show()