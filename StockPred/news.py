import requests
from bs4 import BeautifulSoup

class FinancialNewsFetcher:
    def __init__(self):
        self.url = "https://www.moneycontrol.com/news/business/"

    def fetch_news(self):
        articles = []
        try:
            response = requests.get(self.url)
            soup = BeautifulSoup(response.content, "html.parser")
            headlines = soup.find_all("li", class_="clearfix")

            for headline in headlines:
                title_tag = headline.find("h2") or headline.find("h3")
                if title_tag:
                    title = title_tag.text.strip()
                    link = headline.find("a")["href"]
                    articles.append({
                        "title": title,
                        "url": link,
                        "description": "",
                        "urlToImage": ""
                    })
        except Exception as e:
            print("Error fetching financial news:", e)

        return articles
