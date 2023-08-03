import tensorflow as tf
import tensorflow.keras as keras
from sklearn.ensemble import RandomForestRegressor

# We implement the models used by CDSBen.
# To predict the IOPS sequence, we use a conditional residual RNN (CondResRNN).
# To initialize the states of RNN, we use a simple DNN (InitStateNN).
# Since RNN needs an initial sequence as input, we implement another
# simple RNN (InitNN) to predict the initial sequence.
# For the joint distribution, we use RnadomForestRegressor.


def InitNNLoss(y1, y2):
    """
    This the loss function used for the training of InitNN.
    :param y1:
    :param y2:
    :return:
    """
    v1 = tf.math.reduce_std(y1)
    v2 = tf.math.reduce_std(y2)
    return keras.metrics.mae(tf.sort(y1), tf.sort(y2)) + tf.math.abs(v1 - v2)


def InitNN(units, cond_l):
    inputs = keras.Input(shape=[cond_l])
    l1 = keras.layers.Dense(units=units * 2, activation='relu')(inputs)
    l2 = keras.layers.Dense(units=units * 2, activation='relu')(l1)
    l3 = keras.layers.Dense(units=units, activation='linear')(l2)
    outputs = l3
    model = keras.Model(inputs=inputs, outputs=[outputs])
    return model


def InitStateNN(units, cond_l):
    """
    This model is not used individually in CDSBen.
    It is used as the conditional net of RNN.
    :param units:
    :param cond_l:
    :return:
    """
    inputs = keras.Input(shape=[cond_l])
    l1 = keras.layers.Dense(units=units, activation='tanh')(inputs)
    l2 = keras.layers.Dense(units=units, activation='linear')(l1)
    outputs = l2
    model = keras.Model(inputs=[inputs], outputs=[outputs])
    return model


def CondResRNN(units, window_l, timestamp_l, cond_l):
    """
    We use MAE to train CondResRNN.
    :param units:
    :param window_l:
    :param timestamp_l:
    :param cond_l:
    :return:
    """
    x_inputs = keras.Input(shape=[None, 1])
    c_inputs = keras.Input(shape=[cond_l])
    x_inputs_reshape = keras.layers.Reshape([1, 50])(x_inputs)
    init_state_00 = InitStateNN(units=units, cond_l=cond_l)(c_inputs)
    init_state_01 = InitStateNN(units=units, cond_l=cond_l)(c_inputs)
    lstm00, h0, c0 = keras.layers.LSTM(
        units=units,
        input_shape=[None, timestamp_l],
        return_sequences=True,
        return_state=True,
        activation='relu')(x_inputs_reshape,
                           initial_state=[init_state_00, init_state_01])
    lstm01, h1, c1 = keras.layers.LSTM(units=units,
                                       input_shape=[None, timestamp_l],
                                       return_sequences=True,
                                       return_state=True,
                                       activation='relu')(
                                           lstm00, initial_state=[h0, c0])
    lstm02, h2, c2 = keras.layers.LSTM(units=units,
                                       input_shape=[None, timestamp_l],
                                       return_sequences=True,
                                       return_state=True,
                                       activation='relu')(
                                           lstm01, initial_state=[h1, c1])
    lstm03, _, _ = keras.layers.LSTM(units=units,
                                     input_shape=[None, timestamp_l],
                                     return_sequences=True,
                                     return_state=True,
                                     activation='relu')(lstm02,
                                                        initial_state=[h2, c2])
    lstm04 = keras.layers.LSTM(
        units=window_l,
        input_shape=[None, timestamp_l],
        return_sequences=True,
        activation='relu',
        kernel_regularizer=tf.keras.regularizers.L1(0.01),
        activity_regularizer=tf.keras.regularizers.L2(0.01))(lstm03)
    lstm_out = keras.layers.Reshape([1, 50])(lstm04)
    lstm_out = lstm_out + x_inputs_reshape
    lstm_out = keras.layers.Dense(units=50)(lstm_out)
    lstm_out = keras.layers.Flatten()(lstm_out)
    outputs = lstm_out
    model = keras.Model(inputs=[x_inputs, c_inputs], outputs=[outputs])
    return model


def JointDistRegressor():
    regressor = RandomForestRegressor(n_estimators=1200,
                                      bootstrap=True,
                                      verbose=1,
                                      n_jobs=12,
                                      oob_score=True,
                                      max_features=0.5)
    return regressor