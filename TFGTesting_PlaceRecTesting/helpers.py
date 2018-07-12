
import numpy as np
import pandas as pd


def getClosestReferenceLabels(input_labels, reference_labels):

	trueLabels = []
	reference_labels  = np.array(reference_labels)
	for inputLabel in input_labels:

		diff = abs(inputLabel - reference_labels)
		idx = np.argmin(diff)
		trueLabels.append(reference_labels[idx])

	return trueLabels

def getImage(sequenceFolder, date, labels):

	data = pd.read_csv(sequenceFolder + '/info.csv', header=0)

	data = np.array(data)
	data = data[data[:,0] == int(date),:] #

	imNames = []
	count = 0
	oldName = []
	for label in labels:

		name = data[data[:,-1] == label,2]

		if len(name) == 1:
			count = 0

		if len(name) > 1 and set(oldName) == set(name) and count < len(name)-1:
			count += 1
		else:
			count = 0

		oldName = name
		imNames.append(name[count])

	return imNames

def getLengthOfSequence(path):

	data = pd.read_csv(path + '/info.csv', header=0)

	length = len(np.unique(data['imageName']))

	return length

def getLabels(path, date):

	data = pd.read_csv(path + '/info.csv', header=0)
	data = np.array(data)

	data = data[data[:,0] == int(date),:]

	labels = data[:,-1]

	return labels


def getDates(path):

	dates = []

	file = open(path + "/dates.txt")

	for line in file:
		dates.append(line[:-1])

	return dates

# This function is used to find out if the correct predicted place is between the 20 or the 50 nearest places
#   It takes into account the number of frames considered as the same place (5 in this case)
def posicionPrimerMatch(voted_labels, real_place):
	voted_labels = voted_labels.astype(int)
	encontrado = 0
	ventana = -2
	posicion = -2
	while encontrado == 0:
		posicionMatch = np.where(voted_labels == real_place+ventana)
		if ( np.size(posicionMatch) != 0):
			if ( posicionMatch[0][0] <= 20 ):
				encontrado = 1
				#print(" Encontrado match < 20")
				posicion = 20
				return posicion
			elif ( posicionMatch[0][0] <= 50 ):
				posicion = 50
				#print("Encontrado 50")
		if ( ventana == 4 ):
			encontrado = 1
		ventana += 1
	#print(" Encontrado match < 50")
	return posicion