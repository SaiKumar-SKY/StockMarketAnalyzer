#!/usr/bin/env python3
"""
News Fetcher

Fetches financial news headlines for target stocks from free sources,
performs sentiment analysis, and aggregates daily sentiment scores.
"""

import argparse
import hashlib
import logging
import os
from datetime import datetime, date
from typing import List, Dict, Any

import nltk
import pandas as pd
import yfinance as yf
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download VADER lexicon if not present
try:
    nltk.data.find("vader_lexicon")
except LookupError:
    nltk.download("vader_lexicon")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("news_fetcher.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Constants
NEWS_DIR = "data/news"
FEATURES_DIR = "data/features/sentiment"


class NewsFetcher:
    """Handles fetching news headlines and sentiment analysis."""

    def __init__(self, tickers: List[str]):
        self.tickers = tickers
        self.sid = SentimentIntensityAnalyzer()
        self.news_dir = NEWS_DIR
        self.features_dir = FEATURES_DIR
        os.makedirs(self.news_dir, exist_ok=True)
        os.makedirs(self.features_dir, exist_ok=True)

    def fetch_news_for_ticker(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetch news for a single ticker using yfinance."""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            logger.info(f"Fetched {len(news)} news items for {ticker}")
            return news
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}")
            return []

    def analyze_sentiment(self, headline: str) -> float:
        """Analyze sentiment of a headline using VADER."""
        scores = self.sid.polarity_scores(headline)
        return scores["compound"]

    def process_news(self) -> pd.DataFrame:
        """Fetch and process news for all tickers."""
        all_news = []
        seen_urls = set()

        for ticker in self.tickers:
            news_items = self.fetch_news_for_ticker(ticker)
            for item in news_items:
                content = item.get("content", {})
                url = content.get("canonicalUrl", {}).get("url", "")
                url_hash = hashlib.md5(url.encode()).hexdigest()

                if url_hash in seen_urls:
                    continue
                seen_urls.add(url_hash)

                headline = content.get("title", "")
                source = content.get("provider", {}).get("displayName", "")
                pub_date_str = content.get("pubDate", "")
                published_at = 0
                if pub_date_str:
                    try:
                        published_at = int(
                            datetime.fromisoformat(
                                pub_date_str.replace("Z", "+00:00")
                            ).timestamp()
                        )
                    except (ValueError, AttributeError):
                        published_at = 0

                sentiment = self.analyze_sentiment(headline)

                all_news.append(
                    {
                        "ticker": ticker,
                        "headline": headline,
                        "source": source,
                        "published_at": published_at,
                        "url": url,
                        "sentiment_score": sentiment,
                    }
                )

        df = pd.DataFrame(all_news)
        logger.info(f"Processed {len(df)} unique news items")
        return df

    def save_news(self, df: pd.DataFrame, target_date: date = None):
        """Save news data to CSV."""
        if target_date is None:
            target_date = date.today()
        filename = f"news_{target_date}.csv"
        filepath = os.path.join(self.news_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Saved news to {filepath}")

    def aggregate_sentiment(
        self, df: pd.DataFrame, target_date: date = None
    ) -> pd.DataFrame:
        """Aggregate daily sentiment scores per ticker."""
        if df.empty:
            # Create NaN entries for all tickers
            agg_df = pd.DataFrame(
                {
                    "ticker": self.tickers,
                    "sentiment": [float("nan")] * len(self.tickers),
                }
            )
        else:
            # Group by ticker and compute mean sentiment score
            agg_df = df.groupby("ticker")["sentiment_score"].mean().reset_index()
            agg_df.rename(columns={"sentiment_score": "sentiment"}, inplace=True)
            # Ensure all tickers are present
            all_tickers_df = pd.DataFrame({"ticker": self.tickers})
            agg_df = all_tickers_df.merge(agg_df, on="ticker", how="left")
            agg_df["sentiment"] = agg_df["sentiment"].fillna(float("nan"))

        if target_date is None:
            target_date = date.today()
        filename = f"sentiment_{target_date}.csv"
        filepath = os.path.join(self.features_dir, filename)
        agg_df.to_csv(filepath, index=False)
        logger.info(f"Saved sentiment aggregation to {filepath}")
        return agg_df

    def run(self, target_date: date = None):
        """Main run method."""
        df = self.process_news()
        self.save_news(df, target_date)
        self.aggregate_sentiment(df, target_date)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch financial news and analyze sentiment."
    )
    parser.add_argument(
        "--tickers", nargs="+", required=True, help="List of stock tickers"
    )
    parser.add_argument(
        "--date", type=str, help="Target date in YYYY-MM-DD format (default: today)"
    )

    args = parser.parse_args()

    target_date = None
    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d").date()

    fetcher = NewsFetcher(args.tickers)
    fetcher.run(target_date)


if __name__ == "__main__":
    main()
