'''
Triplet training with Resnet50
'''
from __future__ import absolute_import
from __future__ import print_function

from keras.models import Model
from keras.layers import Input, Lambda, merge
from keras.optimizers import Adam

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import numpy as np

from sklearn.utils import shuffle

from networks import initializeModel
from helpers import getAllFeatures, formatData, loadFeature, getTriplet

####################
# Define network
####################

cityPath = "../../../datasets/BostonFeatures/"

inputSize = 224*224
lr_init = 0.00001
epochs = 20
batchSize = 32

# Initialize model
model,input_neut,processed_neut = initializeModel(inputSize, lr_init)

# Network training using train_on_batch

historial_loss = []
n_iters_lr_decay = 0

data = getAllFeatures(cityPath)
data = formatData(data)
data = shuffle(data)

nLabels = len(data) # length of data

for epoch in range(0, epochs):

    # We use each feature as anchor feature
    for labelIndex in range(nLabels):

        # get a new anchor feature
        neutralRelativeIdx,neutralLabel,neutralPath = data[labelIndex,:]

        # and load this feature
        neutralFeature = loadFeature(neutralPath, neutralRelativeIdx)

        # We find all triplets n positives and n negatives
        positiveRelativeIdxs, positiveLabels, positvePaths, negativeRelativeIdxs, negativeLabels, negativePaths = getTriplet(data,neutralLabel,neutralPath)

        # Number of positive and negative features
        nPositive, nNegative = len(positiveLabels),len(negativeLabels)
        pCounter, nCounter = 0,0

        # Initialize batch and weights
        batch = np.zeros(shape=(batchSize, 3, inputSize), dtype=np.float32)
        weights = np.ones(shape=(batchSize), dtype=np.uint8) # Have no influence on result. Just a hack.

        batchIndex = 0

        # We fill n batch with unique combinations of triplets
        # And train the model for each batch
        for pCounter in range(nPositive):

            # Load a positive feature
            positiveRelativeIdx, positivePath = positiveRelativeIdxs[pCounter], positvePaths[pCounter]
            positiveFeature = loadFeature(positivePath, positiveRelativeIdx)

            for nCounter in range(nNegative):

                # Load a negative feature
                negativeRelativeIdx, negativePath =  negativeRelativeIdxs[nCounter], negativePaths[nCounter]
                negativeFeature = loadFeature(negativePath, negativeRelativeIdx)

                # Add a triplet to batch

                batch[batchIndex, 0] = positiveFeature
                batch[batchIndex, 1] = neutralFeature
                batch[batchIndex, 2] = negativeFeature

                batchIndex += 1

                # We only train if we have a full batch. This might mean that there are some data we do not look at.
                # It could be implemented that the last batch was smaller (the size of the remainder of combinations).
                if batchIndex >= batchSize: # Batch is full

                    loss = model.train_on_batch([batch[:, 0], batch[:, 1], batch[:, 2]], weights) #weight is not used for anything

                    # Save loss
                    historial_loss.append(loss)

                    # Reset batch
                    batch = np.zeros(shape=(batchSize, 3, inputSize), dtype=np.float32)
                    batchIndex = 0

                    n_iters_lr_decay += 1

                    # Decay learning rate
                    if n_iters_lr_decay >= 26000:
                        lr_init = lr_init*0.5
                        model.lr = lr_init
                        n_iters_lr_decay = 0
                        print("Learning rate updated to: ", model.lr)

        # Print status
        if labelIndex % 1000 == 0:
            print("CurrentIndex", labelIndex, " / ", nLabels, " Loss = ", loss)

    # Print status
    print('epoch {}/{}'.format(epoch+1, epochs))
    # We save the version of the model used to execute a single copy of the network
    model2 = Model(input=input_neut, output=[processed_neut])
    model2.save('triplet_resnet23_fc_256_lr' + str(model.lr) + '_adam_norelu_default_Bias0_drop3_' + str(epoch+1) + '_epochs.h5')

###########################################################################
# To obtain a more reliable metric you have to operate with the network
# The previous metric is just comparing ready-made pairs
# We want to compare the distance of each test image with all the others

# We save the version of the model used to execute a single copy of the network
model2 = Model(input=input_neut, output=[processed_neut])
model2.save('triplet_vgg16_prueba.h5')

# We show the evolution of the loss in training

N = 100 # length of running mean

plt.plot(np.linspace(0,len(historial_loss),1),historial_loss,'-o')
mean = np.convolve(np.array(loss), np.ones((N,))/N, mode='valid')
plt.plot(np.linspace(0,len(historial_loss),len(mean)),mean,'r-o')
plt.legend(['loss per batch','running mean of loss per 100 batch'])
plt.show()
