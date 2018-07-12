import numpy as np
import pandas as pd

# This function calculates the euclidean distance between the input vector and all the reference vectors
#   It returns the labels of the closest places
def closestPlaces (vector_caracts, vectores_ref, labs_ref, num_neighbors):

	# Initialization
    distances = np.zeros(vectores_ref.shape[0]) # distances to each reference vector

	# If the size of the feature vector is too big, calculate the euclidean distance in batches
    option = 0

    if option == 0:
        distances[:] = np.sqrt(np.sum( (vectores_ref - vector_caracts)**2, axis = 1))

    """ DONT KNOW THE PURPOSE OF THIS CHUNCK
    if option == 0:
        distances[:] = np.sqrt(np.sum( (vectores_ref - vector_caracts)**2, axis = 1))
        #distancias[:] = cosine_distance(vector_caracts, vectores_ref)
    elif option == 1:
        test_size = vectores_ref.shape[0]
        paso = int(test_size/2)
        distances[0:paso] = np.sqrt(np.sum( (vectores_ref[0:paso]-vector_caracts)**2, axis = 1))
        distances[paso:test_size] = np.sqrt(np.sum( (vectores_ref[paso:test_size]-vector_caracts)**2, axis = 1))
    elif option == 2:
        test_size = vectores_ref.shape[0]
        distances[0:test_size/4] = np.sum(((vectores_ref[:,0:test_size/4]-vector_caracts))**2, axis = 1)
        distances[test_size/4:test_size/2] = np.sum( ((vectores_ref[:,test_size/4:test_size/2]-vector_caracts))**2, axis = 1)
        distances[test_size/2:test_size/2+test_size/4] = np.sum( ((vectores_ref[:,test_size/2:test_size/2+test_size/4]-vector_caracts))**2, axis = 1)
        distances[test_size/2+test_size/4:test_size] = np.sum( ((vectores_ref[:,test_size/2+test_size/4:test_size]-vector_caracts))**2, axis = 1) 
    """
	# Order them with a dataframe
    distance_frame = pd.DataFrame(data={"dist": distances, "idx": labs_ref})
    distance_frame.sort_values("dist", inplace=True)

	# Output the labels of the reference places ordered by similarity to the input place
    nearest_places = distance_frame.iloc[:]["idx"].values

    distances_to_places = distance_frame.iloc[:]["dist"].values

    return nearest_places, distances_to_places


# This function takes the closest places and calculates the number of correct ones
#    It takes into account the number of neighbours considered and outputs the number of correct places in the K nearest places
def correctVotes(neighbors, closestMatches, trueClass):
    votedClass = closestMatches.astype(int)
    nVecesClaseVotada = np.bincount(votedClass[0:neighbors])
    correctVotes = 0
    for votes in range(5):
        if (len(nVecesClaseVotada) >= trueClass-1+votes):
            if trueClass-2+votes >= 0:
                correctVotes +=  nVecesClaseVotada[trueClass-2+votes]
    #print(correctVotes)
    return correctVotes

# This function calculates the cosine distance (not used)
def cosine_distance(vec1, vec2):

    cos_dist = 1.0 - (np.sum(vec1*vec2, axis = 1))/(np.sqrt(np.sum(vec1**2))*np.sqrt(np.sum(vec2**2, axis = 1)))
    return cos_dist

