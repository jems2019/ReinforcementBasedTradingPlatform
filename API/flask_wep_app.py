import google

from flask import Flask, request, jsonify
# import future
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import nltk
import warnings
import json
import pdb
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from flask_restful import Api, Resource, reqparse

import random
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.sectorperformance import SectorPerformances

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

warnings.filterwarnings('ignore')
nltk.download('vader_lexicon')
sent_analysis = SentimentIntensityAnalyzer()

# setup Firestore DB
# Use a service account
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)


@app.route('/get_stock', methods=['GET'])
def get():
    args = request.args
    start_year = int(args['start_year'])
    end_year = int(args['end_year'])
    start_month = int(args['start_month'])
    end_month = int(args['end_month'])
    start_day = int(args['start_day'])
    end_day = int(args['end_day'])
    ticker = args['ticker']

    sentiment_crawler = SentimentCrawler(start_year=start_year, end_year=end_year,
                                         start_month=start_month, end_month=end_month,
                                         start_day=start_day, end_day=end_day,
                                         ticker=str(ticker),
                                         path_to_save_csv='~/')
    sentiment = sentiment_crawler.sentiment_dataframe_creation()

    new_data = RealTimeApi(symbol=ticker)
    new_stock_data = new_data.create_real_time_stock_dataframe()

    combine = CombineSentimentAndRealTimeData(sentiment_data=sentiment, stock_data=new_stock_data)
    combined_data_set = combine.combine_data()
    combined_data_set = combined_data_set.to_json(date_format='iso')

    convert_back = json.loads(combined_data_set)
    new_df = pd.DataFrame.from_dict(convert_back, orient="columns")
    new_df['Date'] = [datetime.strptime(date[0:10], '%Y-%m-%d').date() for date in new_df['Date']]

    new_stock_data = new_df
    print(new_df)
    return combined_data_set


# root
@app.route("/")
def index():
    """
    this is a root dir of my server
    :return: str
    """
    return "This is root!!!!"


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
        response['found'] = True
        for doc in docs:
            response[doc.id] = doc.to_dict()
            print(u'{} => {}'.format(doc.id, doc.to_dict()))
    except google.cloud.exceptions.NotFound:
        response['found'] = False
        print(u'No such documents!')
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


class SentimentCrawler(object):

    def __init__(self, start_year, end_year, start_month,
                 end_month, start_day, end_day, ticker,
                 path_to_save_csv):
        self.start_day = start_day
        self.end_day = end_day
        self.start_month = start_month
        self.end_month = end_month
        self.start_year = start_year
        self.end_year = end_year
        self.ticker = ticker
        self.save_path = path_to_save_csv

    def sentiment_dataframe_creation(self):
        """
        Crawler function that gathers data from market watch.
        :return:
        """
        year_list = range(self.start_year, self.end_year + 1)
        month_list = range(self.start_month, self.end_month + 1)
        day_list = range(self.start_day, self.end_day + 1)

        data = []
        iter_ct = 0

        for year in year_list:
            for month in month_list:
                for day in day_list:
                    print("Month: {month}, Day: {day}, Year: {year}".format(month=str(month),
                                                                            day=str(day),
                                                                            year=str(year)))
                    iter_ct += 1
                    print("Current Count of iterations: {}".format(str(iter_ct)))

                    url = 'https://www.marketwatch.com/search?q=APPL&m=Keyword&rpp=15&mp=806&bd=true&bd=false&bdv={m}%2F{d}%2F{y}&rs=true'.format(
                        ticker=self.ticker, m=month, d=day, y=year)
                    print(url)

                    # url = 'https://www.marketwatch.com/search?q=AAPL&m=Keyword&rpp=15&mp=2005&bd=true&bd=false&bdv=1%2F3%2F2020&rs=true'
                    response = requests.get(url)
                    content = BeautifulSoup(response.content, "html.parser")

                    for news in content.findAll('div', attrs={"class": "searchresult"}):
                        date = content.find('div', attrs={"class": "deemphasized"}).text.encode('utf-8')
                        news = news.text
                        clean_date = self._date_clean_up(date=date)
                        sentiment_score = sent_analysis.polarity_scores(news.rstrip().lstrip())['compound']
                        data.append((clean_date, news.rstrip().lstrip(), sentiment_score))

        return self._make_sent_dataframe_from_crawler(data)

    def _make_sent_dataframe_from_crawler(self, data):
        """
        Creating a dataframe from list of crawler data
        :param data: list: Crawler data
                    Format of the dataframe:
                        - Index column: Date as format YYYY-MM-DD
                        - Sentiment Score: Average per day of sentiment score
                        - Articles: Article that was collected from the crawler
        :return: Dataframe: Average sentiment per day
                            - Format: Index: Date: YYYY-MM-DD
                                      Sentiment Score: Daily average average
        """
        collected_sent_data = pd.DataFrame(data, columns=['Date', 'Articles', 'Sentiment Score'])
        collected_sent_data.drop(labels='Articles', axis=1, inplace=True)
        collected_sent_data = collected_sent_data.set_index(pd.DatetimeIndex(collected_sent_data['Date']))
        average_daily_sentiment = collected_sent_data.resample('D').mean()
        csv_path = '{root}/{ticker}_sentiment.csv'.format(root=self.save_path, ticker=self.ticker)
        print("Saving the sentiment {path} to disk".format(path=csv_path))
        average_daily_sentiment.to_csv(csv_path, sep=',')
        return average_daily_sentiment

    @staticmethod
    def _date_clean_up(date):
        """
        Function to take in date from crawler, which is date published, and converts to match the date format of the
        stock data.
        :param date: Date returned from the crawler
        :return: Clean date in YYYY-MM-DD
        """
        month_base_string = {'Dec.': 'Dec', 'Jan.': 'Jan', 'Feb.': 'Feb', 'March': 'Mar', 'April': 'Apr',
                             'May': 'May', 'June': 'Jun', 'July': 'Jul', 'Aug.': 'Aug', 'Sept.': 'Sept',
                             'Oct.': 'Oct', 'Nov.': 'Nov'}

        clean_date = '{year}-{month}-{day}'.format(year=date.splitlines()[0].decode().split(' ')[2:][2],
                                                   month=month_base_string[date.splitlines()
                                                                           [0].decode().split(' ')[2:][0]],
                                                   day=date.splitlines()[0].decode().split(' ')[2:][1])
        return clean_date


class RealTimeApi(object):

    def __init__(self, symbol, api_key='KHMFAMB5CA0XGKXO'):
        self.api_key = api_key
        self.ticker = symbol
        self.ts = TimeSeries(api_key)
        self.ti = TechIndicators(api_key)
        self.sp = SectorPerformances(api_key)
        self.counter = 0
        self.MAX_API_CALL = 500

    def create_real_time_stock_dataframe(self):
        """
        Take the return of the real time stock api call and converts the return into a dataframe
        :return: Dataframe of new stock data
        """
        real_time_data = self.get_time_series_daily()[0]
        column_list = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        new_stock_data = []
        for sd in real_time_data:
            date = sd.split(' ')[0]
            new_stock_data.append((date, real_time_data[sd]['1. open'],
                                   real_time_data[sd]['2. high'],
                                   real_time_data[sd]['3. low'],
                                   real_time_data[sd]['4. close'],
                                   real_time_data[sd]['5. volume']))

        return pd.DataFrame(new_stock_data, columns=column_list)

    def _counter(self):
        """
        Utility function that keeps track of how many API calls are made. Limit is
        5 per minute and no more then 500 per day per api_key. This function only
        will track api calls and raise an exception when the count reaches the max
        count of 500.
        """
        self.counter += 1
        if self.counter <= self.MAX_API_CALL:
            print('{} API calls have been made. There are {} API calls left for '
                  + 'the day'.format(self.counter, (self.MAX_API_CALL - self.counter)))
            pass
        else:
            print('You have reached the limit of the API calls of {} '
                  + 'for the day.'.format(self.MAX_API_CALL))
            raise ValueError('Too many API calls have been made today.')

    def _get_counter(self):
        return 'Current API call counter is at: {}'.format(self.counter)

    def get_time_series_intraday(self, interval='15min', outputsize='compact',
                                 datatype='json'):
        """
        This API returns intraday time series (timestamp, open, high, low, close,
        volume) of the equity specified. API Parameters
        Required: symbol
            The name of the equity of your choice. For example: symbol=MSFT

        Required: interval
            Time interval between two consecutive data points in the time series.
            The following values are supported: 1min, 5min, 15min, 30min, 60min

        Optional: outputsize
            By default, outputsize=compact. Strings compact and full are accepted
            with the following specifications: compact returns only the latest 100
            data points in the intraday time series; full returns the full-length
            intraday time series. The "compact" option is recommended if you would
            like to reduce the data size of each API call.

        Optional: datatype
            By default, datatype=json. Strings json and csv are accepted with the
            following specifications: json returns the intraday time series in JSON
            format; csv returns the time series as a CSV (comma separated value)
            file.
        """
        self._counter()
        try:
            data, meta_data = self.ts.get_intraday(symbol=self.ticker,
                                                   interval=interval,
                                                   outputsize=outputsize)
        except:
            raise Exception('API call get_intraday failed.')
        return data, meta_data

    def get_time_series_daily(self, outputsize='compact', datatype='json'):
        """
        This API returns daily time series (date, daily open, daily high, daily low,
        daily close, daily volume) of the global equity specified, covering 20+
        years of historical data. The most recent data point is the prices and
        volume information of the current trading day, updated realtime.

        API Parameters
        Required: symbol
            The name of the equity of your choice. For example: symbol=MSFT

        Optional: outputsize
            By default, outputsize=compact. Strings compact and full are accepted
            with the following specifications: compact returns only the latest 100
            data points; full returns the full-length time series of 20+ years of
            historical data. The "compact" option is recommended if you would like
            to reduce the data size of each API call.

        Optional: datatype
            By default, datatype=json. Strings json and csv are accepted with the
            following specifications: json returns the daily time series in JSON
            format; csv returns the time series as a CSV (comma separated value)
            file.
        """
        self._counter()
        try:
            data, meta_data = self.ts.get_daily(symbol=self.ticker,
                                                outputsize=outputsize)
        except:
            raise Exception('API call get_daily failed')

        return data, meta_data

    def get_time_series_daily_adjusted(self, outputsize='compact',
                                       datatype='json', ):
        """
        This API returns daily time series (date, daily open, daily high, daily low,
         daily close, daily volume, daily adjusted close, and split/dividend events)
          of the global equity specified, covering 20+ years of historical data.
        The most recent data point is the prices and volume information of the
        current trading day, updated realtime.

        API Parameters
        Required: symbol
           The name of the equity of your choice. For example: symbol=MSFT

        Optional: outputsize
            By default, outputsize=compact. Strings compact and full are accepted
            with the following specifications: compact returns only the latest 100
            data points; full returns the full-length time series of 20+ years of
            historical data. The "compact" option is recommended if you would
            like to reduce the data size of each API call.

        Optional: datatype
            By default, datatype=json. Strings json and csv are accepted with the
            following specifications: json returns the daily time series in JSON
            format; csv returns the time series as a CSV (comma separated value)
            file.
        """
        self._counter()
        try:
            data, meta_data = self.ts.get_daily_adjusted(symbol=self.ticker,
                                                         outputsize=outputsize,
                                                         datatype=datatype)
        except:
            raise Exception('API call get_daily_adjusted failed')

        return data, meta_data

    def get_simple_moving_average(self, interval='daily',
                                  time_period=20,
                                  series_type='close',
                                  datatype='json'):
        """
        This API returns the simple moving average (SMA) values. See also:
        Investopedia article and mathematical reference.

        API Parameters
        Required: symbol
            The name of the security of your choice. For example: symbol=MSFT

        Required: interval
            Time interval between two consecutive data points in the time series.
            The following values are supported: 1min, 5min, 15min, 30min, 60min,
            daily, weekly, monthly

        Required:time_period
            Number of data points used to calculate each moving average value.
            Positive integers are accepted (e.g., time_period=60, time_period=200)

        Required: series_type
            The desired price type in the time series. Four types are supported:
            close, open, high, low

        Optional: datatype
            By default, datatype=json. Strings json and csv are accepted with the
            following specifications: json returns the daily time series in JSON
            format; csv returns the time series as a CSV (comma separated value)
            file.
        """
        self._counter()
        try:
            data, meta_data = self.ti.get_sma(symbol=self.ticker,
                                              interval=interval,
                                              time_period=time_period,
                                              series_type=series_type,
                                              datatype=datatype)
        except:
            raise Exception('API call simple_moving_average failed')

        return data, meta_data

    def get_exponential_moving_average(self, interval='daily',
                                       time_period=20,
                                       series_type='close',
                                       datatype='json'):
        """
        This API returns the exponential moving average (EMA) values.
        API Parameters
        Required: symbol
           The name of the security of your choice. For example: symbol=MSFT

        Required: interval
            Time interval between two consecutive data points in the time series.
            The following values are supported: 1min, 5min, 15min, 30min, 60min,
            daily, weekly, monthly

        Required:time_period
            Number of data points used to calculate each moving average value.
            Positive integers are accepted (e.g., time_period=60, time_period=200)

        Required: series_type
            The desired price type in the time series. Four types are supported:
            close, open, high, low

        Optional: datatype
            By default, datatype=json. Strings json and csv are accepted with the
            following specifications: json returns the daily time series in JSON
            format; csv returns the time series as a CSV (comma separated value)
            file.
        """
        self._counter()
        try:
            data, meta_data = self.ti.get_ema(symbol=self.ticker,
                                              interval=interval,
                                              time_period=time_period,
                                              series_type=series_type,
                                              datatype=datatype)
        except:
            raise Exception('API call exponential_moving_average failed')

        return data, meta_data

    def get_moving_average_conv_div(self, interval='daily',
                                    series_type='close',
                                    fastperiod=12,
                                    slowperiod=26,
                                    signalperiod=9,
                                    datatype='json'):
        """
        This API returns the moving average convergence / divergence (MACD) values.

        API Parameters
        Required: symbol
            The name of the security of your choice. For example: symbol=MSFT

        Required: interval
            Time interval between two consecutive data points in the time series.
            The following values are supported: 1min, 5min, 15min, 30min, 60min,
            daily, weekly, monthly

        Required: series_type
            The desired price type in the time series. Four types are supported:
            close, open, high, low

        Optional: fastperiod
            Positive integers are accepted. By default, fastperiod=12.

        Optional: slowperiod
            Positive integers are accepted. By default, slowperiod=26.

        Optional: signalperiod
            Positive integers are accepted. By default, signalperiod=9.

        Optional: datatype
            By default, datatype=json. Strings json and csv are accepted with the
            following specifications: json returns the daily time series in JSON
            format; csv returns the time series as a CSV (comma separated value)
            file.
        """
        self._counter()
        try:
            data, meta_data = self.ti.get_macd(symbol=self.ticker,
                                               interval=interval,
                                               series_type=series_type,
                                               fastperiod=fastperiod,
                                               slowperiod=slowperiod,
                                               signalperiod=signalperiod,
                                               datatype=datatype)
        except:
            raise Exception('API call get_moving_average_conv_div failed')

        return data, meta_data

    def get_stochastic_oscillator(self, interval='daily',
                                  fastkperiod=5,
                                  slowkperiod=3,
                                  slowdperiod=3,
                                  slowkmatype=0,
                                  slowdmatype=0,
                                  datatype='json'):
        """
        This API returns the stochastic oscillator (STOCH) values.

        API Parameters
        Required: symbol
            The name of the security of your choice. For example: symbol=MSFT

        Required: interval
            Time interval between two consecutive data points in the time series.
            The following values are supported: 1min, 5min, 15min, 30min, 60min,
            daily, weekly, monthly

        Optional: fastkperiod
            The time period of the fastk moving average. Positive integers are
            accepted. By default, fastkperiod=5.

        Optional: slowkperiod
            The time period of the slowk moving average. Positive integers are
            accepted. By default, slowkperiod=3.

        Optional: slowdperiod
          The time period of the slowd moving average. Positive integers are
          accepted. By default, slowdperiod=3.

        Optional: slowkmatype
            Moving average type for the slowk moving average. By default,
            slowkmatype=0. Integers 0 - 8 are accepted with the following mappings.
                0 = Simple Moving Average (SMA),
                1 = Exponential Moving Average (EMA),
                2 = Weighted Moving Average (WMA),
                3 = Double Exponential Moving Average (DEMA),
                4 = Triple Exponential Moving Average (TEMA),
                5 = Triangular Moving Average (TRIMA),
                6 = T3 Moving Average,
                7 = Kaufman Adaptive Moving Average (KAMA),
                8 = MESA Adaptive Moving Average (MAMA).

        Optional: slowdmatype
        Moving average type for the slowd moving average. By default, slowdmatype=0.
        Integers 0 - 8 are accepted with the following mappings.
            0 = Simple Moving Average (SMA),
            1 = Exponential Moving Average (EMA),
            2 = Weighted Moving Average (WMA),
            3 = Double Exponential Moving Average (DEMA),
            4 = Triple Exponential Moving Average (TEMA),
            5 = Triangular Moving Average (TRIMA),
            6 = T3 Moving Average,
            7 = Kaufman Adaptive Moving Average (KAMA),
            8 = MESA Adaptive Moving Average (MAMA).

        Optional: datatype
            By default, datatype=json. Strings json and csv are accepted with the
            following specifications: json returns the daily time series in JSON
            format; csv returns the time series as a CSV (comma separated value)
            file.
        """
        self._counter()
        try:
            data, meta_data = self.ti.get_stoch(symbol=self.ticker,
                                                interval=interval,
                                                fastkperiod=fastkperiod,
                                                slowkperiod=slowkperiod,
                                                slowdperiod=slowdperiod,
                                                slowkmatype=slowkmatype,
                                                slowdmatype=slowdmatype,
                                                datatype=datatype)
        except:
            raise Exception('API call get_moving_average_conv_div failed')

        return data, meta_data

    def get_bollinger_bands(self, interval='daily',
                            time_period=20,
                            series_type='close',
                            nbdevup=2,
                            nbdevdn=2,
                            matype=0,
                            datatype='json'):
        """
        This API returns the Bollinger bands (BBANDS) values.

        API Parameters
        Required: symbol
           The name of the security of your choice. For example: symbol=MSFT

        Required: interval
            Time interval between two consecutive data points in the time series.
            The following values are supported: 1min, 5min, 15min, 30min, 60min,
            daily, weekly, monthly

        Required:time_period
            Number of data points used to calculate each BBANDS value. Positive
            integers are accepted (e.g., time_period=60, time_period=200)

        Required: series_type
            The desired price type in the time series. Four types are supported:
            close, open, high, low

        Optional: nbdevup
            The standard deviation multiplier of the upper band. Positive integers
            are accepted. By default, nbdevup=2.

        Optional: nbdevdn
           The standard deviation multiplier of the lower band. Positive integers
           are accepted. By default, nbdevdn=2.

        Optional: matype
            Moving average type of the time series. By default, matype=0.
            Integers 0 - 8 are accepted with the following mappings.
            0 = Simple Moving Average (SMA),
            1 = Exponential Moving Average (EMA),
            2 = Weighted Moving Average (WMA),
            3 = Double Exponential Moving Average (DEMA),
            4 = Triple Exponential Moving Average (TEMA),
            5 = Triangular Moving Average (TRIMA),
            6 = T3 Moving Average,
            7 = Kaufman Adaptive Moving Average (KAMA),
            8 = MESA Adaptive Moving Average (MAMA).

        Optional: datatype
            By default, datatype=json. Strings json and csv are accepted with the
            following specifications: json returns the daily time series in JSON
            format; csv returns the time series as a CSV (comma separated value)
            file.
        """
        self._counter()
        try:
            data, meta_data = self.ti.get_bbands(symbol=self.ticker,
                                                 interval=interval,
                                                 time_period=time_period,
                                                 series_type=series_type,
                                                 nbdevup=nbdevup,
                                                 nbdevdn=nbdevdn,
                                                 matype=matype,
                                                 datatype=datatype)
        except:
            raise Exception('API call get_bollinger_bands failed')

        return data, meta_data

    def get_Chaikin_A_D_line(self, interval='daily',
                             datatype='json'):

        """
        This API returns the Chaikin A/D line (AD) values.

        API Parameters
        Required: symbol
            The name of the security of your choice. For example: symbol=MSFT

        Required: interval
            Time interval between two consecutive data points in the time series.
            The following values are supported: 1min, 5min, 15min, 30min, 60min,
            daily, weekly, monthly

        Optional: datatype
            By default, datatype=json. Strings json and csv are accepted with the
            following specifications: json returns the daily time series in JSON
            format; csv returns the time series as a CSV (comma separated value)
            file.
        """
        self._counter()
        try:
            data, meta_data = self.ti.get_ad(symbol=self.ticker,
                                             interval=interval,
                                             datatype=datatype)
        except:
            raise Exception('API call get_Chaikin_A_D_line failed')

        return data, meta_data

    def get_balance_volume(self, interval='daily', datatype='json'):
        """
        This API returns the on balance volume (OBV) values.

        API Parameters
        Required: symbol
            The name of the security of your choice. For example: symbol=MSFT

        Required: interval
            Time interval between two consecutive data points in the time series.
            The following values are supported: 1min, 5min, 15min, 30min, 60min,
            daily, weekly, monthly

        Optional: datatype
            By default, datatype=json. Strings json and csv are accepted with the
            following specifications: json returns the daily time series in JSON
            format; csv returns the time series as a CSV (comma separated value)
            file.
        """
        self._counter()
        try:
            data, meta_data = self.ti.get_obv(symbol=self.ticker,
                                              interval=interval,
                                              datatype=datatype)
        except:
            raise Exception('API call get_balance_volume failed')

        return data, meta_data

    def get_sector_performance(self):
        """
        This API returns the realtime and historical sector performances calculated
        from S&P500 incumbents.
        """
        self._counter()
        try:
            data, meta_data = self.sp.get_sector()
        except:
            raise Exception('API call get_sector_performance failed')

        return data, meta_data


class CombineSentimentAndRealTimeData(object):

    def __init__(self, sentiment_data, stock_data):
        self.sentiment_data = sentiment_data
        self.stock_data = stock_data

    def combine_data(self):
        """
        Function to combine stock and sentiment dataframes
        :return: Combined dataframe
        """
        format = '%Y-%m-%d'
        self.stock_data['Date'] = pd.to_datetime(self.stock_data['Date'], format=format)
        merge_data = pd.merge(self.sentiment_data, self.stock_data, on='Date')
        merge_data.fillna(inplace=True, value=0)

        return merge_data


if __name__ == '__main__':
    # app.add_resource(GetStock, '/get_stock', endpoint='get_stock')
    app.run(host='0.0.0.0', port=5000)



