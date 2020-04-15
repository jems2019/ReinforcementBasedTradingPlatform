
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

        self.scaling_df = pd.DataFrame()
        self.history_df = pd.DataFrame()

        self.last_ticker = ''
        self.last_day = ''

    def _scale_df(self, target_df):
        price_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close']
        high = self.scaling_df['High'].max()
        low = self.scaling_df['Adj Close'].min()
        diff = high - low

        #scale stock info by same scales
        target_df[price_columns] = target_df[price_columns].applymap(lambda x: ((x-low)/diff))

        #scale volume by itself
        scaler = MinMaxScaler()
        scaler.fit(self.scaling_df['Volume'].to_numpy().reshape(-1, 1))
        target_df['Volume'] = scaler.transform(target_df['Volume'].to_numpy().reshape(-1, 1))

        return target_df


    def get_action_from_sent(self, ticker, day, sentiment_df):

        day = datetime.strptime(day, '%Y-%m-%d').strftime('%Y-%m-%d')

        #if the historical data doesnt match the ticker and day
        if not((self.last_ticker == ticker) and (self.last_day == day)):
            print('building historical data in sent')
            self.build_history(ticker, day)

        #merge historical data and sentiment data
        obs_df = pd.merge(self.history_df, sentiment_df, on='Date')
        obs_df.fillna(inplace=True, value=0)

        #make lstm prediction data
        pred_df = self.pred_model.predict(ticker, day, self.obs_len//2)

        #combine historical data and prediction data
        obs_df = obs_df.append(pred_df, ignore_index=True)
        # set sentiment for future pred at 0
        obs_df.fillna(inplace=True, value=0)

        #scale data
        obs_df = self._scale_df(obs_df)
        print(obs_df)

        #rearrange input to match the training data
        col_order = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Sentiment Score']
        obs_df = obs_df[col_order]

        #make rl prediction
        action, _states = self.rl_model.predict(obs_df)

        return action 



    # this method wraps data collection and prediction into one method
    def get_action(self, ticker, day):

        day = datetime.strptime(day, '%Y-%m-%d').strftime('%Y-%m-%d')

        #if the historical data doesnt match the ticker and day
        if not((self.last_ticker == ticker) and (self.last_day == day)):
            print('building historical data')
            self.build_history(ticker, day)

        #get sentiment
        sentiment_df = self.sent_crawler.get_sentiment(ticker, self.history_df.index)

        return self.get_action_from_sent(ticker, day, sentiment_df)


    #builds the historical portion of the stock data using yahoo datareader
    #This call should be done before calling any of the get_action variants, but it should handle fine with last

    #returns - datetime index to use for getting sentiment from firebase for historical data
    def build_history(self, ticker, day):

        self.last_ticker = ticker
        self.last_day = datetime.strptime(day, '%Y-%m-%d').strftime('%Y-%m-%d')

        #get data
        history_start_date = datetime.strptime(day, '%Y-%m-%d') - timedelta(days=self.obs_len)

        self.scaling_df =  DataReader(ticker, 'yahoo', start=self.scaling_start_date)
        self.history_df =  DataReader(ticker, 'yahoo', start=history_start_date, end=day)
        self.history_df = self.history_df.tail(self.obs_len//2)

        # print(self.history_df)
        # print(sent_df)

        #returns index to get correct sentiment from firebase
        return self.history_df.index





# test_model = RLModel(cycle_base_model, lstm)
# test_model.get_action('AAPL', '2019-01-01')