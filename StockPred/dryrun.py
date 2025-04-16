import yfinance as yf

# Define the stock symbol for SBI (State Bank of India)
symbol = "SBIN.NS"

try:
    # Fetch stock data
    stock = yf.Ticker(symbol)
    stock_info = stock.info

    # Print basic stock info
    print("\nStock Details:")
    print(f"Symbol: {stock_info.get('symbol', symbol)}")
    print(f"Name: {stock_info.get('shortName', 'Unknown')}")
    print(f"Current Price: INR {stock_info.get('currentPrice', 'N/A')}")
    print(f"Open Price: INR {stock_info.get('open', 'N/A')}")
    print(f"Day High: INR {stock_info.get('dayHigh', 'N/A')}")
    print(f"Day Low: INR {stock_info.get('dayLow', 'N/A')}")
    print(f"Previous Close: INR {stock_info.get('previousClose', 'N/A')}")
    print(f"Market Cap: {stock_info.get('marketCap', 'N/A')}")
    print(f"Volume: {stock_info.get('volume', 'N/A')}")

    # Fetch last 7 days history
    history = stock.history(period="7d")

    # Check if history is empty
    if history.empty:
        print("\nNo historical data found for this stock.")
    else:
        print("\nLast 7 Days Closing Prices:")
        print(history[['Close']])

except Exception as e:
    print("\nError fetching stock data:", str(e))
