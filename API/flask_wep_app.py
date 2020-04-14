import warnings
warnings.filterwarnings('ignore')
#load model stuff
from RLModel import *
from LSTMStockPrediction import *
from SentimentCrawler import *
from API_crawler import RealTimeApi

import google

import tensorflow as tf

from flask import Flask, request, jsonify
# import future
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import nltk
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from flask_restful import Api, Resource, reqparse

import random
import numpy as np
import pandas as pd

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# print('loading lstm...')    
# tf_model = load_model('./models/LSTM_model_4.h5')
# lstm_model = LSTMStockPrediction(tf_model)

print('loading ppo2...')
ppo2_model = PPO2.load('./models/aapl_trained_model_sent_real_pred.zip')

print('loading sentiment...')
sent_crawler = SentimentCrawler()

#create RL model with other pieces
# rl_model = RLModel(ppo2_model, lstm_model, sent_crawler)

# rl_model.get_action('AAPL', '2020-01-01')

# setup Firestore DB
# Use a service account
print('setup firebase...')
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

# root
@app.route("/")
def index():
    """
    this is a root dir of my server
    :return: str
    """
    return "This is root!!!!"

# get prediction from model
@app.route('/api/get_rl_action/', methods=["GET"])
def get_rl_action():
    print('got request')
    ticker = str(request.args.get('ticker'))
    date = str(request.args.get('date'))

    # need to load lstm in method since tf doesnt like loading outside
    print('loading lstm...')    
    tf_model = load_model('./models/LSTM_model_4.h5')
    lstm_model = LSTMStockPrediction(tf_model)

    rl_model = RLModel(ppo2_model, lstm_model, sent_crawler)

    rl_action = rl_model.get_action(ticker, date)

    print('\n\n\n')
    print(rl_action)

    action_type = np.argmax(rl_action[0:2])
    action_dict = {0:'buy', 1:'sell', 2:'hold'}
    response = {
        'action': action_dict[action_type],
        'percent': str(rl_action[3])
    }


    return jsonify(response)

@app.route('/api/get_id_data/', methods=["GET"])
def get_rt_data():
    # Gets intra day stock data for given ticker symbol. It is 1 min data increments.
    print('Request received. Getting intra day stock data ')
    ticker = str(request.args.get('ticker'))
    data = RealTimeApi(symbol=ticker)
    rt_data = data.get_intra_day_data(interval='1min')
    # get latest stock price in 1 min intervals
    rt_data = rt_data.iloc[:1].to_json()
    return rt_data


@app.route('/api/check_user/<userId>', methods=["GET"])
def check_user_exists(userId):
    doc_ref = db.collection(u'users').document(userId)
    response = {'found': False}
    try:
        doc = doc_ref.get()
        if doc.exists:
            response['found'] = True
            response.update(doc.to_dict())
            print(u'Document data: {}'.format(doc.to_dict()))
        else:
            response['found'] = False
            doc_ref.set({
                u'stocks': []
            })
            print(u'No such document!')
    except google.cloud.exceptions.NotFound:
        response['found'] = False
        doc_ref.set({
            u'stocks': []
        })
        print(u'No such document!')
    return jsonify(response)


@app.route('/api/get_portfolio_data/<userId>', methods=["GET"])
def get_portfolio_data(userId):
    response = {'found': False}
    #stocks collection ref
    stocks_ref = db.collection("stocks")
    #Create stock query to query by userId
    query = stocks_ref.where(u'userId', '==', userId)
    try:
        docs = query.get()
        for doc in docs:
            response[doc.id] = doc.to_dict()
            print(u'{} => {}'.format(doc.id, doc.to_dict()))
    except google.cloud.exceptions.NotFound:
        response['found'] = False
        print(u'No such document!')
    return jsonify(response)



@app.route('/api/create_transaction', methods=['POST'])
def create_transaction():
    json = request.get_json()
    print(json)
    db.collection("transactions").add(
        {
            # u'userId': json['userId'],
            # u'stockTicker': json['stockTicker'],
            # u'amount': json['amount'],
            # u'loss': json['percentLoss'],
            u'sharesHeld': u'200',
            u'timestamp': firestore.SERVER_TIMESTAMP
        }
    )
    return jsonify({'you sent this': ''})


# GET
@app.route('/users/<user>')
def hello_user(user):
    """
    this serves as a demo purpose
    :param user:
    :return: str
    """
    return "Hello %s!" % user


# POST
@app.route('/api/post_some_data', methods=['POST'])
def get_text_prediction():
    """
    predicts requested text whether it is ham or spam
    :return: json
    """
    json = request.get_json()
    print(json)
    if len(json['text']) == 0:
        return jsonify({'error': 'invalid input'})

    return jsonify({'you sent this': json['text']})



if __name__ == '__main__':
    # app.add_resource(GetStock, '/get_stock', endpoint='get_stock')
    app.run(host='0.0.0.0', port=5000)



