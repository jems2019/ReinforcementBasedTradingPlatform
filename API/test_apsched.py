from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

import google

import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def read_from_firebase(date):
    data = []
    sent_ref = db.collection("sentiment")
    docs = sent_ref.where(u'date', u'==', date).stream()

    for doc in docs:
        #put sentiment for current stock into df
        data.append(doc.to_dict()['AAPL']) 

    print('here')
    print(data)
    

#scheduler
sched = BackgroundScheduler(daemon=True)
sched.add_job(read_from_firebase, args=['2020-04-13'], trigger='interval', seconds=30)
sched.start()

#firebase
print('setup firebase...')
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()





app = Flask(__name__)

if __name__ == "__main__":
    app.run('0.0.0.0',port=5000)
