import pickle
import numpy as np
import tensorflow as tf

def load_model(filename):
    """
    This functions loads a saved model

    Arguments:
    filename -- name of the file from where to load the model

    Return:
    model -- the loaded model from file
    """

    try:
        model = tf.keras.models.load_model(filename)
        return model
    except FileNotFoundError:
        pass

def load_scaler(filename):
    """
    This functions loads a saved scaler

    Arguments:
    filename -- name of the file from where to load the scaler

    Return:
    scaler -- the loaded scaler from file
    """

    try:
        file = open(filename, 'rb')
        scaler = pickle.load(file)
        return scaler
    except FileNotFoundError:
        pass
