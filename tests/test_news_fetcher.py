#!/usr/bin/env python3
"""
Unit tests for news_fetcher.py
"""

import os
import tempfile
import unittest
from datetime import date
from unittest.mock import patch, MagicMock
import pandas as pd

from src.news_fetcher import NewsFetcher


class TestNewsFetcher(unittest.TestCase):

    def setUp(self):
        self.tickers = ["AAPL", "MSFT"]
        self.fetcher = NewsFetcher(self.tickers)
        self.temp_dir = tempfile.mkdtemp()
        # Override dirs to temp
        self.fetcher.news_dir = os.path.join(self.temp_dir, "news")
        self.fetcher.features_dir = os.path.join(self.temp_dir, "features", "sentiment")
        os.makedirs(self.fetcher.news_dir, exist_ok=True)
        os.makedirs(self.fetcher.features_dir, exist_ok=True)

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir)

    @patch("src.news_fetcher.yf.Ticker")
    def test_fetch_news_for_ticker_success(self, mock_ticker):
        """Test successful news fetch."""
        mock_stock = MagicMock()
        mock_stock.news = [
            {
                "content": {
                    "title": "Apple news",
                    "provider": {"displayName": "Reuters"},
                    "canonicalUrl": {"url": "http://example.com/1"},
                    "pubDate": "2023-01-01T10:00:00Z",
                }
            },
            {
                "content": {
                    "title": "Apple update",
                    "provider": {"displayName": "Bloomberg"},
                    "canonicalUrl": {"url": "http://example.com/2"},
                    "pubDate": "2023-01-02T10:00:00Z",
                }
            },
        ]
        mock_ticker.return_value = mock_stock

        result = self.fetcher.fetch_news_for_ticker("AAPL")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["content"]["title"], "Apple news")

    @patch("src.news_fetcher.yf.Ticker")
    def test_fetch_news_for_ticker_error(self, mock_ticker):
        """Test news fetch with error."""
        mock_ticker.side_effect = Exception("API error")

        result = self.fetcher.fetch_news_for_ticker("AAPL")
        self.assertEqual(result, [])

    def test_analyze_sentiment(self):
        """Test sentiment analysis."""
        score = self.fetcher.analyze_sentiment("Great news!")
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, -1)
        self.assertLessEqual(score, 1)

    @patch("src.news_fetcher.yf.Ticker")
    def test_process_news(self, mock_ticker):
        """Test processing news with deduplication."""
        mock_stock = MagicMock()
        mock_stock.news = [
            {
                "content": {
                    "title": "Apple news",
                    "provider": {"displayName": "Reuters"},
                    "canonicalUrl": {"url": "http://example.com/1"},
                    "pubDate": "2023-01-01T10:00:00Z",
                }
            },
            {
                "content": {
                    "title": "Apple news",
                    "provider": {"displayName": "Reuters"},
                    "canonicalUrl": {"url": "http://example.com/1"},
                    "pubDate": "2023-01-01T10:00:00Z",
                }
            },
        ]
        mock_ticker.return_value = mock_stock

        df = self.fetcher.process_news()
        self.assertEqual(len(df), 1)  # deduplicated
        self.assertIn("sentiment_score", df.columns)

    def test_save_news(self):
        """Test saving news to CSV."""
        df = pd.DataFrame(
            {
                "ticker": ["AAPL"],
                "headline": ["Test headline"],
                "source": ["Reuters"],
                "published_at": [1640995200],
                "url": ["http://example.com"],
                "sentiment_score": [0.5],
            }
        )
        target_date = date(2023, 1, 1)
        self.fetcher.save_news(df, target_date)

        filepath = os.path.join(self.fetcher.news_dir, "news_2023-01-01.csv")
        self.assertTrue(os.path.exists(filepath))

    def test_aggregate_sentiment_with_data(self):
        """Test sentiment aggregation with data."""
        df = pd.DataFrame(
            {"ticker": ["AAPL", "AAPL", "MSFT"], "sentiment_score": [0.5, 0.7, 0.3]}
        )
        target_date = date(2023, 1, 1)
        agg_df = self.fetcher.aggregate_sentiment(df, target_date)

        self.assertEqual(len(agg_df), 2)
        aapl_sentiment = agg_df[agg_df["ticker"] == "AAPL"]["sentiment"].values[0]
        self.assertAlmostEqual(aapl_sentiment, 0.6)  # (0.5 + 0.7) / 2

        filepath = os.path.join(self.fetcher.features_dir, "sentiment_2023-01-01.csv")
        self.assertTrue(os.path.exists(filepath))

    def test_aggregate_sentiment_no_data(self):
        """Test sentiment aggregation with no data."""
        df = pd.DataFrame()
        target_date = date(2023, 1, 1)
        agg_df = self.fetcher.aggregate_sentiment(df, target_date)

        self.assertEqual(len(agg_df), 2)  # all tickers
        self.assertTrue(pd.isna(agg_df["sentiment"]).all())


if __name__ == "__main__":
    unittest.main()
