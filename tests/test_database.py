#!/usr/bin/env python3
"""
Unit tests for database module (MongoDB).
"""

import unittest
from datetime import datetime, date

from src.database import init_db, get_collection
from src.db_operations import (
    upsert_price,
    upsert_intraday,
    upsert_news,
    upsert_sentiment_feature,
    get_prices,
    get_latest_price,
)


class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        init_db()

    def setUp(self):
        """Clear collections before each test."""
        # Clear collections
        for col_name in [
            "prices",
            "intraday",
            "news",
            "features_sentiment",
            "predictions",
        ]:
            get_collection(col_name).delete_many({})

    def test_upsert_price_new_record(self):
        """Test upserting a new price record."""
        ohlcv = {
            "open": 150.0,
            "high": 155.0,
            "low": 149.0,
            "close": 152.5,
            "volume": 1000000,
        }
        result = upsert_price("AAPL", date(2023, 1, 1), ohlcv)
        self.assertTrue(result)

        latest = get_latest_price("AAPL")
        self.assertIsNotNone(latest)
        self.assertEqual(latest["ticker"], "AAPL")
        self.assertEqual(latest["close"], 152.5)

    def test_upsert_price_duplicate(self):
        """Test upserting duplicate price (should update)."""
        ohlcv = {
            "open": 150.0,
            "high": 155.0,
            "low": 149.0,
            "close": 152.5,
            "volume": 1000000,
        }
        upsert_price("MSFT", date(2023, 1, 1), ohlcv)

        # Upsert with updated values
        ohlcv_updated = {
            "open": 151.0,
            "high": 156.0,
            "low": 150.0,
            "close": 153.5,
            "volume": 1100000,
        }
        result = upsert_price("MSFT", date(2023, 1, 1), ohlcv_updated)
        self.assertTrue(result)

        results = get_prices("MSFT", date(2023, 1, 1), date(2023, 1, 1))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["close"], 153.5)

    def test_upsert_intraday(self):
        """Test upserting intraday price."""
        timestamp = datetime(2023, 1, 1, 10, 0, 0)
        ohlcv = {
            "open": 150.0,
            "high": 151.0,
            "low": 149.5,
            "close": 150.5,
            "volume": 100000,
        }
        result = upsert_intraday("GOOGL", timestamp, ohlcv)
        self.assertTrue(result)

        collection = get_collection("intraday")
        record = collection.find_one({"ticker": "GOOGL"})
        self.assertIsNotNone(record)
        self.assertEqual(record["close"], 150.5)

    def test_upsert_news(self):
        """Test upserting news record."""
        news_record = {
            "ticker": "TSLA",
            "headline": "Tesla announces new product",
            "source": "Reuters",
            "url": "http://example.com/1",
            "published_at": 1672531200,
            "sentiment_score": 0.8,
        }
        result = upsert_news(news_record)
        self.assertTrue(result)

        collection = get_collection("news")
        record = collection.find_one({"ticker": "TSLA"})
        self.assertIsNotNone(record)
        self.assertEqual(record["sentiment_score"], 0.8)

    def test_upsert_sentiment_feature(self):
        """Test upserting sentiment feature."""
        result = upsert_sentiment_feature("NVDA", date(2023, 1, 1), 0.5, 5)
        self.assertTrue(result)

        collection = get_collection("features_sentiment")
        record = collection.find_one({"ticker": "NVDA", "date": "2023-01-01"})
        self.assertIsNotNone(record)
        self.assertEqual(record["sentiment"], 0.5)
        self.assertEqual(record["news_count"], 5)


if __name__ == "__main__":
    unittest.main()
