from keras import backend as K

def euclidean_distance(vects):
    x, y = vects
    return K.sqrt(K.maximum(K.sum(K.square(x - y), axis=1, keepdims=True), K.epsilon()))

def cosine_distance(vects):
    x, y = vects
    return 1.0 - (K.sum(x*y, axis = 1))/(K.sqrt(K.sum(x**2, axis = 1))*K.sqrt(K.sum(y**2, axis = 1)))

def eucl_dist_output_shape(shapes):
    shape1, shape2 = shapes
    return (shape1[0], 1)

def hamming2(s1, s2):
    """Calculate the Hamming distance between two bit strings"""
    assert len(s1) == len(s2)
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))