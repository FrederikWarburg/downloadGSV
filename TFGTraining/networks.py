
from keras.layers import Input,Dropout,Dense, Lambda, merge
from keras import initializers
from keras import Model
from keras.optimizers import Adam

from distanceFunctions import euclidean_distance,eucl_dist_output_shape
from lossFunctions import malaga_loss,identity_loss

def create_base_network(input_shape):
    #Base network to be shared (eq. to feature extraction).

    input = Input(shape=input_shape)

    x = Dropout(0.3, name='drop_2')(input)
    x = Dense(256, name='feat_out_1', bias_initializer=initializers.Constant(value=0.0))(x)

    model = Model(input, x)

    return model

def initializeModel(inputSize, lr_init):

    input_shape = (inputSize,) # Input matrix size
    base_network = create_base_network(input_shape)

    input_pos = Input(shape=input_shape)
    input_neut = Input(shape=input_shape)
    input_neg = Input(shape=input_shape)

    # because we re-use the same instance `base_network`, the weights of the network
    # will be shared across the two branches
    processed_pos = base_network(input_pos)
    processed_neut = base_network(input_neut)
    processed_neg = base_network(input_neg)

    distance_pos = Lambda(euclidean_distance, output_shape=eucl_dist_output_shape)([processed_pos, processed_neut])
    distance_neg = Lambda(euclidean_distance, output_shape=eucl_dist_output_shape)([processed_neg, processed_neut])

    loss = merge(
            [distance_pos, distance_neg],
            mode = malaga_loss,
            name = 'loss',
            output_shape=(1, ))

    model = Model([input_pos, input_neut, input_neg], loss)


    adam = Adam(lr=lr_init, beta_1=0.9, beta_2=0.999, epsilon=0.00000001, decay=0.0, amsgrad=False)

    model.compile(loss = identity_loss, optimizer=adam)

    return model, input_neut, processed_neut
