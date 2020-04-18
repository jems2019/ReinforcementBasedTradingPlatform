
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import logging

from pandas_datareader.data import DataReader

from sklearn.preprocessing import MinMaxScaler

import tensorflow as tf
#import keras

from tensorflow.python.keras.backend import set_session
from tensorflow.python.keras.models import load_model
#from tensorflow.keras.models import load_model


# Method parameters: stock ticker, start date, number of days to predict
# Return: dataframe with predictions

class LSTMStockPrediction():
    # ticker - stock ticker
    # d - day (YYYY-MM-DD) to start the prediction
    # n - number of days to predict starting from date d
    def __init__(self, model, model_path = ''):

        self.session = tf.Session()
        self.graph = tf.get_default_graph()

        with self.graph.as_default():
            with self.session.as_default():
                logging.info("neural network initialised")

        if not (model_path == ''):
            print('loading inside class')
            set_session(self.session)
            self.model = load_model(model_path)
        else:
            self.model = model

        self.history_len = 60
        #self.graph = graph

    def predict(self, ticker, d, n):
        # getting previous 90 days of stock data
        startDate = datetime.strptime(d, '%Y-%m-%d') - timedelta(days=self.history_len+self.history_len)
        # Preparing data for prediction
        data = DataReader(ticker, 'yahoo', start=startDate, end=d)

        # Using last 60 stock data for LSTM model
        inputClosing = data.tail(self.history_len)

        sc = MinMaxScaler(feature_range=(0,1)) # scaling data
        inputClosing_scaled = sc.fit_transform(inputClosing)

        # output list
        out = []

        #for n days, do predictions
        #appends the results for 
        for i in range(n):
            #reshape input for model
            model_input = np.reshape(inputClosing_scaled[i:i+self.history_len,:].T, (data.shape[1],self.history_len,1))
            #do predictions

            
            with self.graph.as_default():
                with self.session.as_default():
                    pred = self.model.predict(model_input)

            #reflip and transform
            predicted_price = sc.inverse_transform(pred.T)
            #put the results to the end of the history array and fix dims
            inputClosing_scaled = np.append(inputClosing_scaled, [pred]).reshape(inputClosing_scaled.shape[0]+1 ,data.shape[1])
            inputClosing_scaled = np.expand_dims(inputClosing_scaled, axis=1)
            #put results to out array
            out.append(predicted_price)

        #convert array to dataframe, use the colums from data
        out = pd.DataFrame(np.concatenate(out), columns=data.columns)
        return out

    def get_session_graph(self):
        return self.session, self.graph


# lstm_model_path = '/content/drive/My Drive/Masters project/LSTM_model_4.h5'
# model = load_model(lstm_model_path)
# lstm = LSTMStockPrediction(model)
# lstm.predict('FB', '2020-01-01', 7)