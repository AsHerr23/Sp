import requests
import pandas as pd
import numpy as np
import tensorflow as tf
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from kiteconnect import KiteConnect
from tensorflow.keras.layers import Conv1D, Dense, Flatten
from gym import Env
from gym.spaces import Discrete, Box
import random
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import tensorflow as tf
print("TensorFlow Version:", tf.__version__)

# 1. Fetch stock data from NSE API
def fetch_nse_data():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return response.json()

# 2. Fetch news data from NewsAPI
def fetch_news():
    API_KEY = "30e48bb7822647ffb8b6c19070cd172a"
    url = f"https://newsapi.org/v2/everything?q=Indian%20Stock%20Market&language=en&sortBy=publishedAt&apiKey={API_KEY}"
    response = requests.get(url)
    return response.json()

# 3. Sentiment Analysis (BERT & VADER)
def analyze_sentiment(news):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_pipeline = pipeline("sentiment-analysis")
    results = []
    for article in news["articles"][:5]:
        headline = article["title"]
        vader_score = analyzer.polarity_scores(headline)["compound"]
        bert_score = sentiment_pipeline([headline])[0]["score"]
        avg_sentiment = (vader_score + bert_score) / 2
        results.append(avg_sentiment)
    return np.mean(results)

# 4. Stock Price Prediction using TCN
def build_tcn_model():
    model = tf.keras.Sequential([
        Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(30, 5)),
        Flatten(),
        Dense(50, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

# 5. Reinforcement Learning Environment (Gym)
class StockTradingEnv(Env):
    def __init__(self):
        self.action_space = Discrete(3)  # Buy, Sell, Hold
        self.observation_space = Box(low=0, high=1, shape=(5,), dtype=np.float32)
        self.current_step = 0
        self.stock_price = np.random.rand(100)

    def step(self, action):
        reward = random.choice([-1, 0, 1])
        self.current_step += 1
        return self.stock_price[self.current_step % 100], reward, self.current_step >= 99, {}

    def reset(self):
        self.current_step = 0
        return self.stock_price[0]

# 6. Portfolio Optimization using RL
def train_rl_model():
    env = StockTradingEnv()
    state = env.reset()
    for _ in range(100):
        action = env.action_space.sample()
        next_state, reward, done, _ = env.step(action)
        if done:
            state = env.reset()

# 7. Deploy with Django (API endpoint example)
from django.http import JsonResponse

def stock_prediction_view(request):
    stock_data = fetch_nse_data()
    news_data = fetch_news()
    sentiment_score = analyze_sentiment(news_data)
    model = build_tcn_model()
    prediction = model.predict(np.random.rand(1, 30, 5))
    return JsonResponse({"prediction": float(prediction), "sentiment": sentiment_score})

# Run all components
data = fetch_nse_data()
news = fetch_news()
sentiment = analyze_sentiment(news)
print("Market Sentiment:", sentiment)
train_rl_model()
