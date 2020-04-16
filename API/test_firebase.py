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
#     sent_ref.document(date).set(data)


try:
    #sent_ref.set(sent_dict)
    query = sent_ref.order_by(u'date', direction=firestore.Query.DESCENDING).limit(3)
    results = query.stream()

    for x in results:
        print(u'{} => {}'.format(x.id, x.to_dict()[ticker]))

except google.cloud.exceptions.NotFound:
    print(u'No such document!')