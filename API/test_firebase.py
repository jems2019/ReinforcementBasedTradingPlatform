from SentimentCrawler import *

import google

import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# setup Firestore DB
# Use a service account
print('setup firebase...')
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

print('loading sentiment...')
sent_crawler = SentimentCrawler()

ticker = 'AAPL'

# sentiment_df = sent_crawler.get_sent_from_range(ticker, '2020-04-10', '2020-04-15')

# print(sentiment_df)
# sent_dict = {}

# for index, row in sentiment_df.iterrows():
#     str_date = index.strftime('%Y-%m-%d')
#     sent_dict[str(str_date)] = row['Sentiment Score']

# print(sent_dict)


sent_ref = db.collection("sentiment")

# for date, score in sent_dict.items():
#     data = {'date':date, ticker:score}
#     sent_ref.document(date).set(data

def auto_trade_user(user_id):

    today = datetime.today().strftime('%Y-%m-%d')

    stocks_ref = db.collection('stocks')
    transactions_ref = db.collection('transactions')

    docs = stocks_ref.where(u'userId', u'==', user_id).stream()

    #for each stock the user has
    for doc in docs:
        balance = doc.to_dict()['cumulativeBalance']
        init_bal = doc.to_dict()['initialBalance']
        min_bal = doc.to_dict()['loss']
        shares_held = doc.to_dict()['totalShares']
        ticker = doc.to_dict()['stockTicker']
        transactions = doc.to_dict()['transactions']

        updated_dict = doc.to_dict()

        print('auto trading ' + user_id + ' stock: ' + ticker + '...')

        rl_action = get_rl_action(ticker, today)

        #get current stock price
        data = RealTimeApi(symbol=ticker)
        rt_data = data.get_intra_day_data(interval='1min')
        #using datareader since other didnt work
        data = DataReader(ticker, 'yahoo', start=today)
        current_price = data.tail(1)['Close']

        if(rl_action['action'] == 'buy'):
            print('i buy')

            total_possible = int(balance / current_price)
            shares_to_buy = int(total_possible * rl_action['percent'])

            cost = shares_to_buy*current_price
            balance -= cost

            trans_dict = {
                'amount' = cost,
                'sharesTransacted' = shares_to_buy,
                'stockTicker' = ticker,
                'timestamp' = firestore.SERVER_TIMESTAMP, 
                'userId' = user_id
                'action_type' = 'buy'
            }

            #add to transaction table
            new_trans = transactions_ref.document()
            trans_id = new_trans.id
            new_trans.set(trans_dict)

            #update stock document
            updated_dict['cumulativeBalance'] = balance
            updated_dict['totalShares'] = shares_held + shares_to_buy
            updated_dict['transactions'].append(trans_id)
            if(balance + current_price*(shares_held + shares_to_buy))<min_bal: 
                updated_dict['auto_trade'] = 'False'     
            stocks_ref.document(user_id).set(updated_dict)


        elif(rl_action['action'] == 'sell'):
            print('i sell')

            shares_to_sell =  int(shares_held * rl_action['percent'])
            cost = shares_to_sell*current_price
            balance += cost
            shares_held -= shares_to_sell

            trans_dict = {
                'amount' = cost,
                'sharesTransacted' = shares_to_sell,
                'stockTicker' = ticker,
                'timestamp' = firestore.SERVER_TIMESTAMP, 
                'userId' = user_id
                'action_type' = 'sell'
            }

            #add to transaction table
            new_trans = transactions_ref.document()
            trans_id = new_trans.id
            new_trans.set(trans_dict)

            #update stock document
            updated_dict['cumulativeBalance'] = balance
            updated_dict['totalShares'] = shares_held + shares_to_buy
            updated_dict['transactions'].append(trans_id)
            if(balance + current_price*(shares_held + shares_to_buy))<min_bal: 
                updated_dict['auto_trade'] = 'False'     
            stocks_ref.document(user_id).set(updated_dict)



    return

auto_trade_user('VIDUggEBiDNs4E2bRFZSUm9mpqN2')