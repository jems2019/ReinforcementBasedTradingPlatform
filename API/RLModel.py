
from datetime import date, datetime, timedelta

import numpy as np
from numpy.random import *
import pandas as pd

from pandas_datareader.data import DataReader

from sklearn.preprocessing import MinMaxScaler

import stable_baselines
from stable_baselines import PPO2
from stable_baselines.common.policies import MlpPolicy

import tensorflow as tf


class RLModel():
    def __init__(self, rl_model, pred_model, sent_crawler):

        self.rl_model = rl_model
        #length of observation
        self.obs_len = 14
        #date for scaling historical data
        self.scaling_start_date = '2016-01-01'

        self.pred_model = pred_model
        self.sent_crawler = sent_crawler

    def _scale_df(self, scaling_df, target_df):
        price_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close']
        high = scaling_df['High'].max()
        low = scaling_df['Adj Close'].min()
        diff = high - low

        #scale stock info by same scales
        target_df[price_columns] = target_df[price_columns].applymap(lambda x: ((x-low)/diff))

        #scale volume by itself
        scaler = MinMaxScaler()
        scaler.fit(scaling_df['Volume'].to_numpy().reshape(-1, 1))
        target_df['Volume'] = scaler.transform(target_df['Volume'].to_numpy().reshape(-1, 1))

        return target_df

    def get_action(self, ticker, day):
        #get data
        history_start_date = datetime.strptime(day, '%Y-%m-%d') - timedelta(days=self.obs_len)

        scaling_df =  DataReader(ticker, 'yahoo', start=self.scaling_start_date)
        history_df =  DataReader(ticker, 'yahoo', start=history_start_date, end=day)
        history_df = history_df.tail(self.obs_len//2)

        #get sentiment for history_df
        sent_df = self.sent_crawler.get_sentiment(ticker, history_df.index)

        # print(history_df)
        # print(sent_df)

        # merge sent and stock together
        history_df = pd.merge(history_df, sent_df, on='Date')
        history_df.fillna(inplace=True, value=0)

        #make lstm prediction data
        pred_df = self.pred_model.predict(ticker, day, self.obs_len//2)

        #combine historical data and prediction data
        obs_df = history_df.append(pred_df, ignore_index=True)
        # set sentiment for future pred at 0
        obs_df.fillna(inplace=True, value=0)

        #scale data
        obs_df = self._scale_df(scaling_df, obs_df)
        print(obs_df)

        #rearrange input to match the training data
        col_order = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Sentiment Score']
        obs_df = obs_df[col_order]

        #make rl prediction
        action, _states = self.rl_model.predict(obs_df)

        return action 





# test_model = RLModel(cycle_base_model, lstm)
# test_model.get_action('AAPL', '2019-01-01')