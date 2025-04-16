import pandas as pd
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima
from pandas.tseries.offsets import BDay

class ArimaStockPredictor:
    def __init__(self, history):
        """Initialize with stock history."""
        self.history = history

    def train_and_forecast(self, days_ahead):
        """Train ARIMA model and forecast stock price for given days ahead."""
        try:
            # Ensure datetime index
            self.history.index = pd.to_datetime(self.history.index)
            # Set frequency to business days if not set
            if self.history.index.freq is None:
                self.history = self.history.asfreq('B')
            # Fill missing values
            self.history.ffill(inplace=True)
            # Use only 'Close' prices
            self.history = self.history[['Close']].dropna()

            if len(self.history) < 60:
                return {"error": "Not enough data for prediction."}

            # Auto ARIMA to select best parameters
            auto_model = auto_arima(
                self.history['Close'],
                seasonal=False,
                stepwise=True,
                suppress_warnings=True,
                error_action='ignore'
            )
            order = auto_model.order
            print(f"Auto ARIMA selected order: {order}")

            # Train ARIMA
            model = ARIMA(self.history['Close'], order=order, trend='t')

            model_fit = model.fit()

            # Forecast
            forecast = model_fit.get_forecast(steps=days_ahead)
            predicted_price = round(forecast.predicted_mean.iloc[-1], 2)

            # Predict date (business day aligned)
            prediction_date = (self.history.index[-1] + BDay(days_ahead)).strftime("%Y-%m-%d")

            return {"days_ahead": days_ahead, "date": prediction_date, "predicted_price": predicted_price}

        except Exception as e:
            return {"error": str(e)}

def fetch_stock_data(ticker="SBIN.NS"):
    """Fetch stock data from Yahoo Finance."""
    stock_data = yf.download(ticker, period="2y", interval="1d", auto_adjust=True)
    return stock_data

if __name__ == "__main__":
    # Fetch data
    history_df = fetch_stock_data("SBIN.NS")
    predictor = ArimaStockPredictor(history_df)

    # Forecast for multiple timeframes
    forecast_days = [5, 10, 30, 100, 200, 500]
    results = []

    for days in forecast_days:
        result = predictor.train_and_forecast(days)
        if "error" not in result:
            results.append(result)
        else:
            print(f"Error for {days} days ahead: {result['error']}")

    # Show forecast results
    forecast_results_df = pd.DataFrame(results)
    print("\nForecast results for multiple timeframes:")
    print(forecast_results_df)
