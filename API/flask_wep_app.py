print('loading libs...')
import warnings

warnings.filterwarnings('ignore')
# load model stuff
from RLModel import *
from LSTMStockPrediction import *
from SentimentCrawler import *
from API_crawler import RealTimeApi

import google
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

app = Flask(__name__)

print('loading lstm...')
tf_model = load_model('./models/LSTM_model_4.h5')
lstm_model = LSTMStockPrediction(tf_model, './models/LSTM_model_4.h5')

print('loading ppo2...')
ppo2_model = PPO2.load('./models/aapl_trained_model_sent_real_pred.zip')

print('loading sentiment...')
sent_crawler = SentimentCrawler()

sentiment_df = pd.DataFrame()

# create RL model with other pieces
rl_model = RLModel(ppo2_model, lstm_model, sent_crawler)

# setup Firestore DB
# Use a service account
print('setup firebase...')
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


# ----helper functions---#

# gets model action using sentiment from firebase
# should add the sentiment to firebase if it's not there
def get_rl_action(ticker, date):
    # load historical data and get range for sentiment
    date_range = rl_model.build_history(ticker, date)
    # empty df with proper indexing
    sentiment_df = pd.DataFrame(index=date_range, columns=['Sentiment Score'])

    # firebase ref
    sent_ref = db.collection("sentiment")

    for index, row in sentiment_df.iterrows():
        str_date = index.strftime('%Y-%m-%d')
        # get the sentiment from firebase for date
        docs = sent_ref.where(u'date', u'==', str_date).stream()
        date_exists = False
        #if date is there, but sent is not
        for doc in docs:
            date_exists = True
            if not (ticker in doc.to_dict().keys()):
                print(str_date + ' ' + ticker + ' sentiment not in firebase, adding it')
                store_sentiment(ticker, str_date, str_date)
        #if no date in firebase
        if not(date_exists):
            print(str_date + ' ' + ticker + ' sentiment not in firebase, adding it')
            store_sentiment(ticker, str_date, str_date)

        # reload docs
        docs = sent_ref.where(u'date', u'==', str_date).stream()
        for doc in docs:
            # put sentiment for current stock into df
            sentiment_df.loc[index, :] = doc.to_dict()[ticker]

    print(sentiment_df)

    rl_action = rl_model.get_action_from_sent(ticker, date, sentiment_df)

    print('\n')
    print(rl_action)

    action_type = np.argmax(rl_action[0:2])
    action_dict = {0: 'buy', 1: 'sell', 2: 'hold'}
    response = {
        'action': action_dict[action_type],
        'percent': str(rl_action[3])
    }

    return response


# gets sentiment and stores it in firebase
def store_sentiment(ticker, start_date, end_date):
    sentiment_df = sent_crawler.get_sent_from_range(ticker, start_date, end_date)

    # convert df to dict to put in firebase
    sent_dict = {}
    for index, row in sentiment_df.iterrows():
        str_date = index.strftime('%Y-%m-%d')
        sent_dict[str(str_date)] = row['Sentiment Score']

    # firebase ref
    sent_ref = db.collection("sentiment")

    # put shit in firebase
    for date, score in sent_dict.items():
        data = {'date': date, ticker: score}
        sent_ref.document(date).set(data, merge=True)

    return


# auto trade based on stock document from firebase
def auto_trade_stock(doc):
    today = datetime.today().strftime('%Y-%m-%d')

    stocks_ref = db.collection('stocks')
    transactions_ref = db.collection('transactions')

    balance = float(doc.to_dict()['balance'])
    init_bal = float(doc.to_dict()['initialBalance'])
    min_bal = float(doc.to_dict()['minBalance'])
    shares_held = int(doc.to_dict()['sharesHeld'])
    ticker = doc.to_dict()['stockTicker']
    transactions = doc.to_dict()['transactions']
    user_id = doc.to_dict()['userId']

    if not (doc.to_dict()['autoTrade']):
        print('AUTO TRADE IS OFF FOR: ' + user_id + ' stock: ' + ticker)
        return

    updated_dict = doc.to_dict()

    print('auto trading ' + user_id + ' stock: ' + ticker + '...')

    rl_action = get_rl_action(ticker, today)

    # get current stock price
    data = RealTimeApi(symbol=ticker)
    rt_data = data.get_intra_day_data(interval='1min')

    # using datareader since other didnt work
    # data = DataReader(ticker, 'yahoo', start=today)
    # current_price = data.tail(1)['Close'][0]

    current_price = float(rt_data.iloc[0]["Close"])

    if (rl_action['action'] == 'buy'):
        print('i buy')

        total_possible = int(balance / current_price)
        shares_to_buy = int(total_possible * float(rl_action['percent']))
        print('buying ' + str(shares_to_buy))

        cost = float(shares_to_buy * current_price)
        balance -= cost

        portfolio_value = current_price * (shares_held + shares_to_buy) + balance

        trans_dict = {
            'amount': float(cost),
            'sharesTransacted': int(shares_to_buy),
            'stockTicker': ticker,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'userId': user_id,
            'portfolioValue': portfolio_value,
            'action_type': 'buy'
        }

        # add to transaction table
        new_trans = transactions_ref.document()
        trans_id = new_trans.id
        new_trans.set(trans_dict)
        print('added transaction')

        # update stock document
        updated_dict['balance'] = balance
        updated_dict['sharesHeld'] = shares_held + shares_to_buy
        updated_dict['transactions'].append(trans_id)
        if (balance + updated_dict['sharesHeld']*current_price) < min_bal:
            updated_dict['autoTrade'] = False
        stocks_ref.document(doc.id).set(updated_dict)
        print('updated stock\n')


    elif (rl_action['action'] == 'sell'):
        print('i sell')

        shares_to_sell = int(shares_held * float(rl_action['percent']))
        print('selling ' + str(shares_to_sell))
        cost = float(shares_to_sell * current_price)
        balance += cost
        shares_held -= shares_to_sell

        portfolio_value = current_price * (shares_held + shares_to_buy) + balance

        trans_dict = {
            'amount': cost,
            'sharesTransacted': shares_to_sell,
            'stockTicker': ticker,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'userId': user_id,
            'portfolioValue': portfolio_value,
            'action_type': 'sell'
        }

        # add to transaction table
        new_trans = transactions_ref.document()
        trans_id = new_trans.id
        new_trans.set(trans_dict)
        print('added transaction')

        # update stock document
        updated_dict['balance'] = balance
        updated_dict['sharesHeld'] = shares_held + shares_to_buy
        updated_dict['transactions'].append(trans_id)
        if (balance + updated_dict['sharesHeld']*current_price) < min_bal:
            updated_dict['autoTrade'] = False
        stocks_ref.document(doc.id).set(updated_dict)
        print('updated stock\n')

    return


# auto trades all stocks owned by user
def auto_trade_user(user_id):
    stocks_ref = db.collection('stocks')
    transactions_ref = db.collection('transactions')

    docs = stocks_ref.where(u'userId', u'==', user_id).stream()

    # for each stock the user has, auto trade
    for doc in docs:
        auto_trade_stock(doc)

    return


# auto trades all the users
def auto_trade_all():
    print('starting auto trading for all users...')
    user_ref = db.collection('users')
    users = user_ref.stream()
    for user in users:
        auto_trade_user(user.id)


def store_test():
    print('storing test')
    test_ref = db.collection('test')
    new_test = test_ref.document()
    new_test.set({'a':'a'})

def test_scheduler():
    print('Testing scheduler at ' + str(datetime.now()))

# ---set up automatic updates---#

# scheduler
sched = BackgroundScheduler(daemon=True)

# set autotrading to happen at noon every day
today = datetime.today().strftime('%Y-%m-%d')
today += ' 12:00:00'
# auto trade all every day at 12 pm
sched.add_job(auto_trade_all, trigger='interval', days=1, start_date=today)
sched.add_job(test_scheduler, trigger='interval', minutes=1, start_date=today)
sched.start()


# ---API functions---#

# root
@app.route("/")
def index():
    """
    this is a root dir of my server
    :return: str
    """
    return "This is root!!!!"


# get prediction from model in one call, should read data from firebase
"""
params - 
ticker: <stock symbol>
date: <date in form YYYY-MM-DD to get a prediction from>

returns - 
action: {'buy', 'sell', 'hold'}
percent: percent of balance/stock to buy/sell
"""


@app.route('/api/get_rl_action/', methods=["GET"])
def api_get_rl_action():
    print('api/get_rl_action')
    ticker = str(request.args.get('ticker'))
    date = str(request.args.get('date'))

    response = get_rl_action(ticker, date)

    return jsonify(response)


# get prediction from model in one call, fetches sentiment on the fly
"""
params - 
ticker: <stock symbol>
date: <date in form YYYY-MM-DD to get a prediction from>

returns - 
action: {'buy', 'sell', 'hold'}
percent: percent of balance/stock to buy/sell
"""


@app.route('/api/get_rl_action_on_fly/', methods=["GET"])
def api_get_rl_action_on_fly():
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


@app.route('/api/auto_trade_user/', methods=["POST"])
def api_auto_trade_user():
    user_id = str(request.args.get('user_id'))
    auto_trade_user(user_id)
    return jsonify({'success': True})


@app.route('/api/auto_trade_user_stock/', methods=["POST"])
def api_auto_trade_user_stock():
    user_id = str(request.args.get('user_id'))
    ticker = str(request.args.get('ticker'))

    stocks_ref = db.collection('stocks')
    transactions_ref = db.collection('transactions')

    docs = stocks_ref.where(u'userId', u'==', user_id).where(u'stockTicker', '==', ticker).stream()

    # for each stock the user has, auto trade
    for doc in docs:
        auto_trade_stock(doc)

    return jsonify({'success': True})


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


# adds a doc to the stock table, updates the repsective user
"""
params - 
userId: <id of user>
ticker: <stock symbol>
amount: starting balance for this stock
minBalance: minimum balance for this stock before autotrade stops

returns - 
success: true or false
"""


@app.route('/api/add_stock_to_user/', methods=['POST'])
def add_stock_to_user():
    print('adding new stock for user')
    new_stock = {
        'userId': request.args.get('userId'),
        'stockTicker': request.args.get('ticker'),
        'sharesHeld': 0,
        'balance': request.args.get('amount'),
        'initialBalance': request.args.get('amount'),
        'minBalance': request.args.get('minBalance'),
        'transactions': [],
        'autoTrade': True
    }

    # update user table
    user_ref = db.collection("users").document(new_stock['userId'])
    user = user_ref.get()
    if user.exists:
        user_ref.update(
            {
                u'stocks': firestore.ArrayUnion([new_stock['stockTicker']])
            }
        )
    else:
        print('no user found')
        return jsonify({'success': False})

    # update stock table
    stocks_ref = db.collection("stocks")
    stocks_ref.document().set(new_stock)

    return jsonify({'success': True})


# Update stock when user has stock in portfolio
"""
params - 
userId: <id of user>
ticker: <stock symbol>
amount: starting balance for this stock
minBalance: minimum balance for this stock before autotrade stops

returns - 
success: true or false
"""


@app.route('/api/update_stock_for_user/', methods=['POST'])
def update_stock_for_user():
    stocks_ref = db.collection("stocks")
    # Create stock query to query by userId and stock ticker
    query = stocks_ref.where(u'userId', '==', request.args.get('userId')).where(u'stockTicker', '==',
                                                                                request.args.get('ticker'))
    try:
        doc_ref = query.get()
        for doc in doc_ref:
            doc_update = stocks_ref.document(doc.id)
            doc_update.update(
                {
                    'balance': firestore.Increment(int(request.args.get('amount'))),
                    'initialBalance': firestore.Increment(int(request.args.get('amount'))),
                    'minBalance': request.args.get('minBalance'),
                }
            )
    except google.cloud.exceptions.NotFound:
        print(u'No such documents!')
        return jsonify({'success': False})
    return jsonify({'success': True})


# Get all transactions
@app.route('/api/get_transactions/', methods=['GET'])
def get_transactions():
    response = {'success': False}
    stocks_ref = db.collection("stocks")
    transactions_ref = db.collection("transactions")
    # Create stock query to query by userId and stock ticker
    query = stocks_ref.where(u'userId', '==', request.args.get('userId')).where(u'stockTicker', '==',
                                                                                request.args.get('ticker'))
    try:
        doc_ref = query.get()
        temp = {}
        for doc in doc_ref:
            transactions = doc.to_dict()['transactions']
            for transactionId in transactions:
                transaction_dict = transactions_ref.document(transactionId).get().to_dict()
                transaction_dict['timestamp'] = str(transaction_dict['timestamp'])
                temp[transactionId] = transaction_dict
        response['transactions'] = temp
        response['success'] = True
    except google.cloud.exceptions.NotFound:
        print(u'No such documents!')
    return json.dumps(response)


# GET
@app.route('/users/<user>')
def hello_user(user):
    """
    this serves as a demo purpose
    :param user:
    :return: str
    """
    return "Hello %s!" % user


# store sentiment data to the firebase
"""
params - 
ticker: <stock symbol>
start_date: <date in form YYYY-MM-DD>
end_date: <date in form YYYY-MM-DD> - forms range to get sentiment from


returns - 
successful on finishing
"""


@app.route('/api/store_sentiment/', methods=["POST"])
def api_store_sentiment():
    ticker = str(request.args.get('ticker'))
    start_date = str(request.args.get('start_date'))
    end_date = str(request.args.get('end_date'))

    store_sentiment(ticker, start_date, end_date)

    return jsonify({'successful': True})


if __name__ == '__main__':
    # app.add_resource(GetStock, '/get_stock', endpoint='get_stock')
    # app.run(host='0.0.0.0', port=5000)
    app.run(debug=True, host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)))
