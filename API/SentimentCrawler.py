from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta

import requests
import nltk
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from pandas_datareader.data import DataReader

import random
import pandas as pd
import numpy as np


class SentimentCrawler():
    def __init__(self):
        nltk.download('vader_lexicon')
        self.sent_analysis = SentimentIntensityAnalyzer()
        self.base_url = 'https://www.marketwatch.com/search?q={ticker}&m=Keyword&rpp=15&mp=806&bd=true&bd=false&bdv={m}%2F{d}%2F{y}&rs=true'

    def get_sent_from_range(self, ticker, start_date, end_date):
        date_range = self._date_range(start_date, end_date)
        return(self.get_sentiment(ticker, date_range))

    def get_sentiment(self, ticker, days):
        data = []

        for cur_date in days:
            year = cur_date.year
            month = cur_date.month
            day = cur_date.day
            
            print(cur_date)
            url = self.base_url.format(ticker=ticker, m=month, d=day, y=year)
            print(url)

            response = requests.get(url)
            content = BeautifulSoup(response.content, "html.parser")

            for news in content.findAll('div', attrs={"class": "searchresult"}):
                try:
                    #date = content.find('div', attrs={"class": "deemphasized"}).text.encode('utf-8')
                    news = news.text
                    #clean_date = self._date_clean_up(date=date)
                    sentiment_score = self.sent_analysis.polarity_scores(news.rstrip().lstrip())['compound']
                    data.append((cur_date, news.rstrip().lstrip(), sentiment_score))
                except:
                    print('Encountered Error')
        
        ave_sentiment = self._make_sent_dataframe_from_crawler(data)

        return ave_sentiment

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

        return average_daily_sentiment


    def _date_range(self, start_date, end_date):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        dates = []
        for n in range(int ((end_date - start_date).days)+1):
            dates.append(start_date + timedelta(n))

        return dates





