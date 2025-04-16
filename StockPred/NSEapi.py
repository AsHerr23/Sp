import requests

def fetch_nse_data():
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36",
        "Referer": "https://www.nseindia.com/",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=10)

    print(f" NSE API Status Code: {response.status_code}")  # Debugging

    if response.status_code != 200:
        print(f"Error: NSE API returned status code {response.status_code}")
        return None

    try:
        data = response.json()
        print(f"NSE API Response: {data}")  # Debugging
        return data
    except requests.exceptions.JSONDecodeError:
        print("Error: NSE API returned invalid JSON.")
        return None

# Run the test
fetch_nse_data()
