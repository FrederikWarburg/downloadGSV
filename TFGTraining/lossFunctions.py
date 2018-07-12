from keras import backend as K

def contrastive_loss(y_true, y_pred):
    '''Contrastive loss from Hadsell-et-al.'06
    http://yann.lecun.com/exdb/publis/pdf/hadsell-chopra-lecun-06.pdf
    '''
    margin = 1
    return K.mean(y_true * K.square(y_pred) +
                  (1 - y_true) * K.square(K.maximum(margin - y_pred, 0)))


def double_contrastive_loss(X):
    '''Contrastive loss from Hadsell-et-al.'06
    http://yann.lecun.com/exdb/publis/pdf/hadsell-chopra-lecun-06.pdf
    '''
    dist_pos, dist_neg = X
    margin = 1.0
    return K.square(dist_pos) + K.square(K.maximum(margin - dist_neg, 0.0))


def malaga_loss(X):
    dist_pos, dist_neg = X
    margin = 1.0
    return K.maximum(0.0, 1.0-dist_neg/(margin + dist_pos))


def identity_loss(y_true, y_pred):
    return K.mean(y_pred - 0 * y_true)
