import feedparser
import yfinance as yf
import pandas as pd
import numpy as np
from fyers_apiv3 import fyersModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from datetime import datetime, timedelta

# -------------------------------
# ✅ Initialize Components
# -------------------------------
# Sentiment Analysis Models
vader = SentimentIntensityAnalyzer()
finbert = pipeline("text-classification", model="ProsusAI/finbert")

# 🔹 Fyers API Credentials (Replace with your own)
CLIENT_ID = "95INC3BKC2-100"
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE3NDEwNzM1MzYsImV4cCI6MTc0MTEzNDYxNiwibmJmIjoxNzQxMDczNTM2LCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCbnhxeUFRSENucXhzb1JvNzl0d0syeW8xaEdyX3lQNm1BNHhVZ0lvaEY2Y1k2Njd3UDludUtrOGFPNGFVYmFGeXdNYk1FNHVzb2VSSmJIQXI1cVhqMWpOYjR2S25CazZHdnNLa1NrSEM5MjRTLUxZMD0iLCJkaXNwbGF5X25hbWUiOiJCSUpBTCBOSUtVTCBQQVRFTCIsIm9tcyI6IksxIiwiaHNtX2tleSI6IjQ2YmZiODhmYjhlYjQxMjU0NDNjNWJmZjJmMDg4Y2MyYzY0ZDMwZjU2NTU4NWQzOGQ0ZDVlYzc1IiwiaXNEZHBpRW5hYmxlZCI6bnVsbCwiaXNNdGZFbmFibGVkIjpudWxsLCJmeV9pZCI6IlhCMDI1MDciLCJhcHBUeXBlIjoxMDAsInBvYV9mbGFnIjoiTiJ9._ZIo5torE6dZ5GDGz9yDDM7eaKi0V-NB8P8KQfDjbu0"

# Initialize Fyers API
fyers = fyersModel.FyersModel(client_id=CLIENT_ID, token=ACCESS_TOKEN, is_async=False, log_path="")

# RSS Feed URLs (Financial News)
RSS_FEEDS = [
    "https://www.business-standard.com/rss/home_page_top_stories.rss",
    "https://www.reutersagency.com/feed/?best-topics=business-finance",
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
]

# Sentiment Thresholds
SENTIMENT_THRESHOLD = 0.5  # Adjust based on testing

# Assets to Monitor
ASSETS = ["NSE:SBIN-EQ", "NSE:TCS-EQ", "NSE:RELIANCE-EQ"]  # Extend as needed


# -------------------------------
# ✅ Step 1: Fetch & Analyze News
# -------------------------------
def fetch_news_from_rss(limit=5):
    """Fetch and parse news articles from multiple RSS feeds."""
    news_items = []
    for feed_url in RSS_FEEDS:
        parsed_feed = feedparser.parse(feed_url)
        for entry in parsed_feed.entries[:limit]:
            news_items.append({
                "title": entry.get("title", "").strip(),
                "summary": entry.get("summary", "").strip(),
                "published": entry.get("published", "").strip()
            })
    return news_items


def analyze_sentiment(text):
    """Analyze sentiment using both VADER & FinBERT."""
    vader_score = vader.polarity_scores(text)["compound"]
    finbert_result = finbert(text[:512])  # Limit input for FinBERT
    finbert_score = 1 if finbert_result[0]['label'].lower() == "positive" else -1 if finbert_result[0][
                                                                                         'label'].lower() == "negative" else 0
    return vader_score, finbert_score


def filter_news_by_sentiment(news_items):
    """Filter news that has a sentiment score above the threshold."""
    filtered_news = []
    for news in news_items:
        sentiment_vader, sentiment_finbert = analyze_sentiment(news["title"] + " " + news["summary"])
        avg_sentiment = (sentiment_vader + sentiment_finbert) / 2  # Combine both models

        if avg_sentiment > SENTIMENT_THRESHOLD:
            filtered_news.append({**news, "sentiment_score": avg_sentiment})

    return filtered_news


# -------------------------------
# ✅ Step 2: Fetch Market Data
# -------------------------------
def fetch_market_data(symbol, start_date, end_date):
    """Fetch historical stock price data."""
    stock = yf.Ticker(symbol.replace("NSE:", ""))  # Convert NSE:SBIN-EQ -> SBIN
    history = stock.history(start=start_date, end=end_date)
    return history


def calculate_price_change(data):
    """Calculate daily % price change for sentiment correlation."""
    data["Price Change (%)"] = data["Close"].pct_change() * 100
    return data


# -------------------------------
# ✅ Step 3: Fetch Order Book & Order Flow (Using Fyers API)
# -------------------------------
def fetch_order_book(symbol):
    """Fetch latest order book snapshot for a stock from Fyers API."""
    data = {"symbol": symbol, "ohlcv_flag": "1"}
    response = fyers.depth(data=data)

    if "d" in response:
        order_book = response["d"]
        return {
            "Bid Price": order_book.get("buy", [{}])[0].get("price", "N/A"),
            "Ask Price": order_book.get("sell", [{}])[0].get("price", "N/A"),
            "Bid Size": order_book.get("buy", [{}])[0].get("quantity", "N/A"),
            "Ask Size": order_book.get("sell", [{}])[0].get("quantity", "N/A")
        }
    return {"Bid Price": "N/A", "Ask Price": "N/A", "Bid Size": "N/A", "Ask Size": "N/A"}


def fetch_order_flow(symbol):
    """Analyze order flow using executed trades from Fyers API."""
    data = {"symbol": symbol}
    response = fyers.market_status()

    if "d" in response:
        order_flow = response["d"]
        total_buys = sum(item.get("buy_quantity", 0) for item in order_flow)
        total_sells = sum(item.get("sell_quantity", 0) for item in order_flow)
        imbalance = total_buys - total_sells
        return {"Total Buys": total_buys, "Total Sells": total_sells, "Imbalance": imbalance}

    return {"Total Buys": "N/A", "Total Sells": "N/A", "Imbalance": "N/A"}


# -------------------------------
# ✅ Step 4: Generate Trading Signals
# -------------------------------
def generate_trade_signal(sentiment_score, price_change, order_imbalance):
    """Generate buy/sell/hold signal based on market sentiment & order flow."""
    if sentiment_score > 0.3 and price_change > 1 and order_imbalance > 50:
        return "BUY"
    elif sentiment_score < -0.3 and price_change < -1 and order_imbalance < -50:
        return "SELL"
    else:
        return "HOLD"


# -------------------------------
# ✅ Step 5: Execute the Trading System
# -------------------------------
def run_trading_system():
    print("\n🚀 Fetching News Data & Analyzing Sentiment...")
    news_items = fetch_news_from_rss()
    filtered_news = filter_news_by_sentiment(news_items)

    if not filtered_news:
        print("⚠️ No high-sentiment news found. No trades executed.")
        return

    print(f"\n✅ {len(filtered_news)} News Items Passed Sentiment Threshold:")
    for news in filtered_news:
        print(f"📢 {news['title']} | Sentiment: {news['sentiment_score']}")

    # Track impacted assets & fetch market data
    from_date = (datetime.today() - timedelta(days=5)).strftime("%Y-%m-%d")
    to_date = datetime.today().strftime("%Y-%m-%d")

    for asset in ASSETS:
        print(f"\n🔍 Processing {asset}")

        # Fetch Market Data
        market_data = fetch_market_data(asset, from_date, to_date)
        market_data = calculate_price_change(market_data)

        if market_data.empty:
            print(f"⚠️ No market data found for {asset}")
            continue

        # Fetch Order Book & Order Flow Data
        order_book = fetch_order_book(asset)
        order_flow = fetch_order_flow(asset)

        # Generate Trading Signal
        latest_price_change = market_data["Price Change (%)"].iloc[-1]
        signal = generate_trade_signal(filtered_news[0]["sentiment_score"], latest_price_change,
                                       order_flow["Imbalance"])

        # Display Results
        print(f"📊 Order Book: {order_book}")
        print(f"📈 Order Flow: {order_flow}")
        print(f"🚀 Trading Signal for {asset}: {signal}")

        # Execute Trade (if required)
        if signal in ["BUY", "SELL"]:
            print(f"🔄 Executing {signal} trade for {asset}... (Paper Trading)")


# -------------------------------
# ✅ Run the Strategy
# -------------------------------
if __name__ == "__main__":
    run_trading_system()
