import warnings
warnings.filterwarnings('ignore')

from RLModel import *
from LSTMStockPrediction import *
from SentimentCrawler import *

print('loading lstm...')
tf_model = load_model('./models/LSTM_model_4.h5')
lstm_model = LSTMStockPrediction(tf_model)

print('loading ppo2...')
ppo2_model = PPO2.load('./models/aapl_trained_model_sent_real_pred.zip')

print('loading sentiment...')
sent_crawler = SentimentCrawler()

rl_model = RLModel(ppo2_model, lstm_model, sent_crawler)

today = datetime.today().strftime('%Y-%m-%d')

print(today)

dates = rl_model.build_history('AAPL', today)

print(dates)

sentiment_df = sent_crawler.get_sent_from_range('AAPL', '2020-04-01', today)

print(sentiment_df.loc[dates])


# print(rl_model.get_action('AAPL', '2020-01-01'))

# print('second pred')

# print(rl_model.get_action('AAPL', '2020-02-01'))


# sent = sent_crawler.get_sent_from_range('AAPL', '2020-04-10', today)

# print(sent)