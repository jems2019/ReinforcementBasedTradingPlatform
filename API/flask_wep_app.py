import warnings

warnings.filterwarnings('ignore')
# load model stuff
from RLModel import *
from LSTMStockPrediction import *
from SentimentCrawler import *
from API_crawler import RealTimeApi

import google
from flask import Flask, request, jsonify
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore



print('loading ppo2...')
ppo2_model = PPO2.load('./models/aapl_trained_model_sent_real_pred.zip')

print('loading sentiment...')
sent_crawler = SentimentCrawler()



# rl_model.get_action('AAPL', '2020-01-01')

# setup Firestore DB
# Use a service account
print('setup firebase...')
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()



# root
@app.route("/")
def index():
    """
    this is a root dir of my server
    :return: str
    """
    return "This is root!!!!"


@app.route('/api/get_rl_action/', methods=["GET"])
def get_rl_action():
    ticker = str(request.args.get('ticker'))
    date = str(request.args.get('date'))



returns - 
action: {'buy', 'sell', 'hold'}
percent: percent of balance/stock to buy/sell
"""
@app.route('/api/get_rl_action_on_fly/', methods=["GET"])
def get_rl_action_on_fly():
    ticker = str(request.args.get('ticker'))
    date = str(request.args.get('date'))

    rl_action = rl_model.get_action(ticker, date)

    print('\n\n\n')
    print(rl_action)

    action_type = np.argmax(rl_action[0:2])
    action_dict = {0: 'buy', 1: 'sell', 2: 'hold'}
    response = {
        'action': action_dict[action_type],
        'percent': str(rl_action[3])
    }

    return jsonify(response)



@app.route('/api/get_id_data/', methods=["GET"])
def get_rt_data():
    dict = {}
    # Gets intra day stock data for given ticker symbol. It is 1 min data increments.
    print('Request received. Getting intra day stock data ')
    ticker = str(request.args.get('ticker'))
    data = RealTimeApi(symbol=ticker)
    rt_data = data.get_intra_day_data(interval='1min')
    # get latest stock price in 1 min intervals
    # rt_data = rt_data.iloc[:1].to_json()
    dict['date'] = rt_data.iloc[0]["Date"]
    dict['open'] = rt_data.iloc[0]["Open"]
    dict['high'] = rt_data.iloc[0]["High"]
    dict['low'] = rt_data.iloc[0]["Low"]
    dict['close'] = rt_data.iloc[0]["Close"]
    dict['volume'] = rt_data.iloc[0]["Volume"]
    print(dict)
    return jsonify(dict)


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
    # stocks collection ref
    stocks_ref = db.collection("stocks")
    # Create stock query to query by userId
    query = stocks_ref.where(u'userId', '==', userId)
    temp = {}
    try:
        docs = query.get()
        response['found'] = True
        for doc in docs:
            temp[doc.id] = doc.to_dict()
            print(u'{} => {}'.format(doc.id, doc.to_dict()))
        response['stocks'] = temp
    except google.cloud.exceptions.NotFound:
        response['found'] = False
        response['stocks'] = temp
        print(u'No such documents!')
    print(response)
    return json.dumps(response)


@app.route('/api/create_transaction', methods=['POST'])
def create_transaction():
    json = request.get_json()
    resp = {}
    doc_ref = db.collection(u'users').document(json['userId'])
    stocks_ref = db.collection("stocks")
    try:
        # Update User stock info
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update(
                {
                    u'stocks': firestore.ArrayUnion([json['stockTicker']])
                }
            )

            # Add transaction to the trasanctions table
            doc_ref = db.collection("transactions").document()
            doc_ref.set(
                {
                    u'userId': json['userId'],
                    u'stockTicker': json['stockTicker'],
                    u'amount': json['amount'],
                    u'sharesHeld': 200,
                    u'timestamp': firestore.SERVER_TIMESTAMP
                }
            )
            doc_id = doc_ref.id
            print(doc_id)
            resp['docId'] = doc_id

            # update Transaction info for stock
            query = stocks_ref.where(u'userId', '==', json['userId']).where(u'stockTicker', '==', json['stockTicker'])
            doc_ref = query.get()
            doc_ref_empty = True
            doc = None
            for document in doc_ref:
                doc_ref_empty = False
                doc = document
            if doc_ref_empty:
                doc_ref = db.collection("stocks").document()
                doc_ref.set(
                    {
                        u'stockTicker': json['stockTicker'],
                        u'userId': json['userId'],
                        u'initialBalance': json['amount'],
                        u'cumulativeBalance': json['amount'],
                        u'loss': json['percentLoss'],
                        u'totalShares': 200,
                        u'transactions': [doc_id]
                    }
                )
                resp['transaction_status'] = 'Created'
            else:
                dict_fields = doc.to_dict()
                print(dict_fields)
                doc.update(
                    {
                        u'cumulativeBalance': json['amount'] + dict_fields['cumulativeBalance'],
                        u'loss': (json['percentLoss'] + dict_fields['loss']) / 2,
                        u'totalShares': 200 + dict_fields['totalShares'],
                        u'transaction': firestore.ArrayUnion([doc_id])
                    }
                )
                resp['transaction_status'] = 'Updated'
        else:
            print(u'No such document!')
    except google.cloud.exceptions.NotFound:
        print(u'No such documents!')
        resp['transaction_status'] = 'Failed'
    return jsonify(resp)


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


def automate_trade():
    return


if __name__ == '__main__':
    # app.add_resource(GetStock, '/get_stock', endpoint='get_stock')
    app.run(host='0.0.0.0', port=5000)
