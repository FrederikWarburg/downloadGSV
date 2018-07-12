import matplotlib.pyplot as plt
import numpy as np
from helpers import measure
import math

def plotInterpolation(pos, lats, lons, orientation = True):

    #if max(pos[:,2]) > 2*math.pi:
    #    pos[:,2] = pos[:,2]*math.pi/180

    us = (pos[:,0] + np.cos(pos[:,2]) / 1000)
    vs = (pos[:,1] + np.sin(pos[:, 2]) / 1000)

    if orientation:
        for i in range(0,pos.shape[0],10):
            plt.plot([pos[i,0], us[i]], [pos[i,1], vs[i]], 'r-')

    plt.plot(pos[:,0],pos[:,1],'b.')
    plt.plot(lats,lons,'ro')
    return plt

def plotPanoidsPosition(gps,pos):
    colors = ['#f44283','#f44283','#f44283','#5b91a0','#632596','#963725','#d6b753', '#20b2aa','#ffc3a0','#fff68f','#f6546a',
        '#468499','#ff6666','#666666','#66cdaa','#c39797','#00ced1','#ff00ff','#008000','#088da5']

    plt.plot(pos[:, 0], pos[:, 1], 'b.')

    for c, date in enumerate(gps):
        obs = gps[date]

        lats = obs['lat']
        lons = obs['lon']

        plt.plot(lats,lons,'o',color=colors[c%len(colors)])

    plt.show()

def getYearsOfSequenceSet(path):

    dates = []

    file = open(path,'r')

    for line in file:
        dates.append(line[:-1])

    file.close()

    return dates


def calculateDistanceOfSequences(allSequences):

    distance = 0
    distancesOfEachSequence = []
    framesOfEachSequence = []

    for sequenceSet in allSequences:

        for sequence in sequenceSet:

            sequenceLength = 0

            for idx in range(len(sequence)-1):

                lat1 = sequence[idx][1]
                lon1 = sequence[idx][2]

                lat2 = sequence[idx+1][1]
                lon2 = sequence[idx+1][2]

                sequenceLength += measure(lat1,lon1,lat2,lon2)

            distancesOfEachSequence.append(sequenceLength/1000) # from m to km
            framesOfEachSequence.append(len(sequence))

        distance += sequenceLength

    distance = distance/ 1000.0 # from m to km

    return distance, distancesOfEachSequence, framesOfEachSequence



