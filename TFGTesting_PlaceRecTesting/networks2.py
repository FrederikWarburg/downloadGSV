import numpy as np

from keras.preprocessing import image

def extractFeatures2(images, model1, model2):

    features = [] # Features for all images
    means = np.array([103.939, 116.779, 123.68])  # Imagenet mean (bgr)

    for im in images:

        # preprocessing of image
        im = image.img_to_array(im)

        # Substract mean of each color channel (check up)
        im[:, :, 2] = im[:, :, 0] - means[2]
        im[:, :, 1] = im[:, :, 1] - means[1]
        im[:, :, 0] = im[:, :, 2] - means[0]

        im = np.expand_dims(im,
                            axis=0)  # Insert a new axis that will appear at the axis position in the expanded array shape.

        # Use resnet to make prediction
        feat_1 = model1.predict(im).flatten()
        feat_1 = np.reshape(feat_1, (1, 50176)) # Process image with pre trained model

        # Use added layers to create feature descriptor
        feat = model2.predict(feat_1)
        feat = np.reshape(feat, (128)) # Process vector with the added layers

        features.append(feat)

    return np.asarray(features)
