import requests
import numpy as np
import tensorflow as tf
from django.http import JsonResponse
from django.shortcuts import render
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.http import HttpResponse

def loginview(requests):
    return render(requests , 'login.html')

def index(request):
    return render(request , "index.html")

def authenticate_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid username or password"})

    return JsonResponse({"status": "error", "message": "Invalid request"})

# Store previous stock data to prevent empty screen on API failure
previous_stock_data = []

# Fetch stock data from NSE API
def fetch_nse_data():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36",
        "Referer": "https://www.nseindia.com/",
        "Accept-Language": "en-US,en;q=0.9",
    }
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)  # Fetch homepage to set cookies
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        print(f"Error: NSE API Unauthorized: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed: {e}")
    return None

# Fetch news and perform sentiment analysis
def fetch_news():
    API_KEY = "30e48bb7822647ffb8b6c19070cd172a"
    url = f"https://newsapi.org/v2/everything?q=Indian%20Stock%20Market&language=en&sortBy=publishedAt&apiKey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            news_data = response.json()
            if "articles" in news_data:
                return news_data
            print("Error: Error: 'articles' key missing in NewsAPI response")
        print(f"Error: Error: NewsAPI returned status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed: {e}")
    return None

def analyze_sentiment(news):
    if not news or "articles" not in news or not news["articles"]:
        print("Error: No news articles available for sentiment analysis")
        return 0, []  # Ensure function always returns two values
    
    analyzer = SentimentIntensityAnalyzer()
    sentiment_pipeline = pipeline("sentiment-analysis")

    sentiment_scores = []
    reasons = []

    for article in news["articles"][:20]:  
        headline = article.get("title", "")
        if not headline:
            continue
        
        vader_score = analyzer.polarity_scores(headline)["compound"]
        bert_result = sentiment_pipeline([headline])[0]
        bert_score = bert_result["score"] if bert_result["label"] == "POSITIVE" else -bert_result["score"]

        avg_sentiment = (vader_score + bert_score) / 2
        sentiment_scores.append(avg_sentiment)
        reasons.append(headline)  # Store news reasons

    # Normalize sentiment score
    final_sentiment = np.clip(np.mean(sentiment_scores), -1, 1) if sentiment_scores else 0

    return final_sentiment, reasons  # Ensure two values are always returned



# Generate Buy/Sell Recommendations
def generate_recommendations(stock_data, sentiment_score,reason):
    if not stock_data or "data" not in stock_data or not stock_data["data"]:
        print("Error: 'data' key not found or empty in stock_data")
        return []

    recommendations = []
    for i, stock in enumerate(stock_data["data"][:20]):  
        stock_name = stock.get("symbol", "Unknown")
        last_price = stock.get("lastPrice", 0)
        open_price = stock.get("open", 0)
        day_high = stock.get("dayHigh", 0)
        day_low = stock.get("dayLow", 0)
        predicted_price = last_price * (1 + np.random.uniform(-0.02, 0.02))

        if sentiment_score > 0.2 and predicted_price > last_price:
            action = "Buy"
        elif sentiment_score < -0.2 and predicted_price < last_price:
            action = "Sell"
        else:
            action = "Hold"

        recommendations.append({
            "stock": stock_name,
            "current_price": last_price,
            "open_price": open_price,
            "day_high": day_high,
            "day_low": day_low,
            "predicted_price": round(predicted_price, 2),
            "action": action,
            
        })

    return recommendations




# API Endpoint
def stock_prediction_view(request):
    stock_data = fetch_nse_data()
    news_data = fetch_news()
    if not stock_data or not news_data:
        return JsonResponse({"error": "Failed to fetch stock or news data"}, status=500)
    sentiment_score, reasons = analyze_sentiment(news_data)
    recommendations = generate_recommendations(stock_data, sentiment_score, reasons)
    return JsonResponse({"sentiment": sentiment_score, "recommendations": recommendations})

# HTML View
def stock_recommendations_page(request):
    stock_data = fetch_nse_data()
    news_data = fetch_news()
    if not stock_data or not news_data:
        print("Error: Error: Failed to fetch stock or news data.")
        return render(request, "home.html", {"recommendations": []})
    sentiment_score, reasons = analyze_sentiment(news_data)
    recommendations = generate_recommendations(stock_data, sentiment_score, reasons)
    return render(request, "home.html", {"recommendations": recommendations})


####################### for stock dashboard##########################################

# View for rendering real-time stock prices
def real_time_stocks(request):
    stock_data = fetch_nse_data()
    if stock_data and "data" in stock_data:
        stocks = stock_data["data"][:10]
    else:
        stocks = []
    return render(request, "stocklist.html", {"stocks": stocks})

# API endpoint for fetching stock data in JSON format
def fetch_stocks(request):
    global previous_stock_data
    stock_data = fetch_nse_data()
    if stock_data and "data" in stock_data:
        previous_stock_data = stock_data["data"][:100]
        return JsonResponse({"stocks": previous_stock_data})
    print("Error: NSE API failed, returning previous stock data")
    return JsonResponse({"stocks": previous_stock_data})



############################################################################################################


from django.shortcuts import render
import yfinance as yf
from datetime import datetime
from .ArimaModel import ArimaStockPredictor

def stock_detail(request, symbol=None):
    stock_data = None
    prediction = None
    error = None

    if request.method == "POST":
        symbol = request.POST.get("symbol")
        selected_date = request.POST.get("date")
    else:
        selected_date = request.GET.get("date", None)

    if symbol:
        try:
            # Fetch stock data
            stock = yf.Ticker(symbol + ".NS")
            stock_info = stock.info
            history = stock.history(period="90d", auto_adjust=True)

            stock_data = {
                "symbol": stock_info.get("symbol", symbol),
                "name": stock_info.get("shortName", "Unknown"),
                "current_price": stock_info.get("currentPrice", "N/A"),
                "open_price": stock_info.get("open", "N/A"),
                "day_high": stock_info.get("dayHigh", "N/A"),
                "day_low": stock_info.get("dayLow", "N/A"),
                "previous_close": stock_info.get("previousClose", "N/A"),
                "market_cap": stock_info.get("marketCap", "N/A"),
                "volume": stock_info.get("volume", "N/A"),
                "history": history[['Close']].dropna().to_dict() if not history.empty else {},
            }

            # Prediction logic
            if selected_date:
                selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
                last_date = history.index[-1].date()
                days_ahead = (selected_date_obj - last_date).days

                if days_ahead > 0:
                    predictor = ArimaStockPredictor(history)
                    prediction = predictor.train_and_forecast(days_ahead)
                else:
                    prediction = {"error": "Selected date must be in the future."}

        except Exception as e:
            error = str(e)

    return render(request, "stockdt.html", {"stock": stock_data, "prediction": prediction, "error": error})

##################model for graph###################3
from django.shortcuts import render
import yfinance as yf
from .AriamaGraph import StockPredictorWithGraph, fetch_stock_data_for_prediction
from datetime import datetime ,timedelta
def stockpred(request):
    prediction = None
    graph_url = None
    error = None
    current_price = None
    current_price_date = None
    stock_name = None
    nse_symbol = None
    prediction_date = None
        time_frame = None

    if request.method == "POST":
        symbol = request.POST.get("symbol")
        days_ahead = request.POST.get("days_ahead")

        try:
            if symbol and days_ahead:
                days_ahead = int(days_ahead)
                nse_symbol = symbol.upper() + ".NS"  # Convert to NSE format

                # Fetch stock details using yfinance
                stock_data = yf.Ticker(nse_symbol)
                stock_info = stock_data.info

                # Get stock name
                stock_name = stock_info.get("longName", "Unknown Stock")

                # Get the latest stock price and its corresponding date
                hist = stock_data.history(period="1d")
                if hist.empty:
                    error = "No current stock price data available."
                else:
                    current_price = hist["Close"].iloc[-1]
                    current_price_date = hist.index[-1].date()

                    # Calculate prediction date
                    prediction_date = current_price_date + timedelta(days=days_ahead)
                    time_frame=days_ahead

                    # Fetch historical stock data for forecasting
                    history = fetch_stock_data_for_prediction(nse_symbol)

                    if history.empty:
                        error = "No historical stock data found for the given symbol."
                    else:
                        predictor = StockPredictorWithGraph(history)
                        result = predictor.train_and_forecast(days_ahead)

                        if "error" in result:
                            error = result["error"]
                        else:
                            prediction = result
                            forecast_series = result["forecast_series"]
                            graph_url = predictor.generate_graphs(forecast_series, symbol, days_ahead)
            else:
                error = "Please provide both a stock symbol and a valid prediction date."

        except Exception as e:
            error = f"An error occurred: {str(e)}"

    return render(request, "stockpred.html", {
        "prediction": prediction,
        "current_price": current_price,
        "current_price_date": current_price_date,
        "stock_name": stock_name,
        "nse_symbol": nse_symbol,
        "graph_url": graph_url,
        "error": error,
        "prediction_date": prediction_date,
        "time_frame": time_frame
    })
#_____________________________________news_______________________________________
from .news import FinancialNewsFetcher
from datetime import datetime

def news(request):
    fetcher = FinancialNewsFetcher()
    articles = fetcher.fetch_news()
    return render(request, 'news.html', {'articles': articles, 'now': datetime.now()})

#_______________________________support_____________________________________________________
def support(request):
    return render(request ,'support.html')



def submit_ticket(request):
    if request.method == 'POST':
        problem = request.POST.get('problem')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        
        # Save ticket data or process it here
        
        return HttpResponse("Support ticket submitted successfully!")
    return render(request, 'raise_ticket.html')
