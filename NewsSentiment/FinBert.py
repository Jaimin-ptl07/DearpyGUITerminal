import feedparser
import yfinance as yf
import spacy
from fuzzywuzzy import process
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
from transformers import pipeline

# ========== SETUP ==========
# Load NLP & Sentiment Analyzer
nlp = spacy.load("en_core_web_sm")
vader = SentimentIntensityAnalyzer()

# Load FinBERT sentiment analysis model
finbert = pipeline("text-classification", model="ProsusAI/finbert")

# RSS Feeds
RSS_FEEDS = [
    "https://www.business-standard.com/rss/home_page_top_stories.rss",
]

feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
# Sample assets (stocks, forex, commodities) - Expand dynamically if needed
ASSETS = ["Apple", "Tesla", "Amazon", "Bitcoin", "Gold", "Oil", "S&P 500", "EUR/USD", "AAPL", "TSLA", "AMZN"]

# ========== FUNCTIONS ==========
def fetch_news(limit=5):
    """Fetch and parse news articles from multiple RSS feeds, including published date."""
    news_items = []

    for feed_url in RSS_FEEDS:
        parsed_feed = feedparser.parse(feed_url)

        for entry in parsed_feed.entries[:limit]:  # Limit to `limit` articles per feed
            title = entry.get("title", "No Title").strip()
            summary = (entry.get("description") or entry.get("summary") or "").strip()
            published = entry.get("published", "No Date Available").strip()

            news_items.append((title, summary, published))

    return news_items

def extract_assets(news_text):
    """Extract assets from news using Named Entity Recognition and fuzzy matching."""
    doc = nlp(news_text)
    found_assets = set()
    for ent in doc.ents:
        best_match = process.extractOne(ent.text, ASSETS, score_cutoff=80)
        if best_match:
            found_assets.add(best_match[0])
    return list(found_assets)

def get_vader_sentiment(text):
    """Lexicon-based Sentiment Analysis using VADER."""
    scores = vader.polarity_scores(text)
    return scores['compound']  # Returns a score between -1 and 1

def get_finbert_sentiment(text):
    """Financial Sentiment Classification using FinBERT."""
    result = finbert(text[:512])  # Limit input to 512 characters for FinBERT
    return result[0]['label'].lower()  # Returns: 'positive', 'negative', or 'neutral'

def get_stock_price(symbol, date):
    """Fetch stock price for a given date."""
    stock = yf.Ticker(symbol)
    history = stock.history(start=date, end=date + timedelta(days=1))
    return history["Close"].iloc[0] if not history.empty else None

def compute_impact(sentiment_score, price_change):
    """Compute impact score based on sentiment and price movement."""
    return round(sentiment_score * price_change * 100, 2)

def process_news():
    """Main function to fetch news, analyze sentiment, track prices, and display results."""
    news_list = fetch_news()

    print("\n🚀 **Financial News Sentiment & Market Impact** 🚀\n")
    for news in news_list[:5]:  # Limit to 5 latest news articles
        title, summary, published = news[0], news[1], news[2]
        assets = extract_assets(title + " " + summary)
        sentiment_score = get_vader_sentiment(title + " " + summary)
        finbert_sentiment = get_finbert_sentiment(title + " " + summary)

        final_sentiment = "positive" if sentiment_score > 0.3 else "negative" if sentiment_score < -0.3 else "neutral"

        # Display News
        print(f"📢 News: {title}")
        print(f"📅 Published: {published}")
        print(f"📰 Summary: {summary[:100]}...")  # Show first 100 chars of summary
        print(f"🔍 Detected Assets: {', '.join(assets) if assets else 'None'}")
        print(f"🧠 Sentiment (VADER): {sentiment_score:.2f} ({final_sentiment.upper()})")
        print(f"🤖 FinBERT Sentiment: {finbert_sentiment.upper()}")

        # Track price movement for detected assets
        impact_scores = {}
        for asset in assets:
            try:
                price_now = get_stock_price(asset, datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z"))
                price_1d = get_stock_price(asset, datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z") + timedelta(days=1))

                if price_now and price_1d:
                    price_change = (price_1d - price_now) / price_now
                    impact_scores[asset] = compute_impact(sentiment_score, price_change)

                    print(f"📊 {asset} - Price at News: ${price_now:.2f}, 1-Day Later: ${price_1d:.2f}, Impact Score: {impact_scores[asset]}")
            except Exception as e:
                print(f"⚠️ Could not fetch price data for {asset}: {e}")

        print("-" * 80)

# ========== EXECUTION ==========
if __name__ == "__main__":
    process_news()
