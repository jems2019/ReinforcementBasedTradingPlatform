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


stock_ref = db.collection('stocks')

trans_ref = db.collection('transactions')

def get_trans(user_id, ticker):
    trans_ref.where('userId', '==', user_id).where('stockTicker', '==', ticker)

