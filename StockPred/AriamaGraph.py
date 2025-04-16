import pandas as pd
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima
from pandas.tseries.offsets import BDay
import matplotlib.pyplot as plt
import io
import base64

class StockPredictorWithGraph:
    def __init__(self, history):
        """Initialize with stock history."""
        self.history = history

    def train_and_forecast(self, days_ahead):
        """Train ARIMA model and forecast stock price for given days ahead."""
        try:
            self.history.index = pd.to_datetime(self.history.index)
            if self.history.index.freq is None:
                self.history = self.history.asfreq('B')
            self.history.ffill(inplace=True)
            self.history = self.history[['Close']].dropna()

            if len(self.history) < 60:
                return {"error": "Not enough data for prediction."}

            auto_model = auto_arima(
                self.history['Close'],
                seasonal=False,
                stepwise=True,
                suppress_warnings=True,
                error_action='ignore'
            )
            order = auto_model.order

            model = ARIMA(self.history['Close'], order=order, trend='t')
            model_fit = model.fit()

            forecast = model_fit.get_forecast(steps=days_ahead)
            predicted_price = round(forecast.predicted_mean.iloc[-1], 2)

            prediction_date = (self.history.index[-1] + BDay(days_ahead)).strftime("%Y-%m-%d")

            forecast_series = forecast.predicted_mean
            return {
                "days_ahead": days_ahead,
                "date": prediction_date,
                "predicted_price": predicted_price,
                "forecast_series": forecast_series
            }

        except Exception as e:
            return {"error": str(e)}

    def generate_graphs(self, forecast_series, symbol, days_ahead):
        """Generate and return graphs as base64 string."""
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(self.history.index, self.history['Close'], label="Historical Price", color='blue')
            forecast_index = pd.date_range(start=self.history.index[-1] + pd.tseries.offsets.BDay(1), periods=days_ahead)
            plt.plot(forecast_index, forecast_series, label=f"Forecast ({days_ahead} days)", color='green')

            plt.title(f"{symbol} Stock Price Forecast")
            plt.xlabel("Date")
            plt.ylabel("Price (₹)")
            plt.legend()
            plt.grid(True)

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()
            plt.close()

            return f"data:image/png;base64,{image_base64}"

        except Exception as e:
            return None

def fetch_stock_data_for_prediction(ticker="SBIN.NS"):
    """Fetch stock data from Yahoo Finance."""
    return yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
