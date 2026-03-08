#!/usr/bin/env python3
"""
Database operations helper functions for MongoDB upsert patterns.
"""

import logging
from datetime import datetime, date
from typing import Any, Dict, List, Optional

from src.database import (
    get_collection,
)

logger = logging.getLogger(__name__)


def upsert_price(ticker: str, price_date: date, ohlcv: Dict[str, Any]) -> bool:
    """Upsert a single price record."""
    try:
        collection = get_collection("prices")
        data = {
            "ticker": ticker,
            "date": price_date.isoformat(),
            "open": ohlcv.get("open"),
            "high": ohlcv.get("high"),
            "low": ohlcv.get("low"),
            "close": ohlcv.get("close"),
            "volume": ohlcv.get("volume", 0),
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = collection.update_one(
            {"ticker": ticker, "date": price_date.isoformat()},
            {
                "$set": data,
                "$setOnInsert": {"created_at": datetime.utcnow().isoformat()},
            },
            upsert=True,
        )
        return result.matched_count > 0 or result.upserted_id is not None
    except Exception as e:
        logger.error(f"Error upserting price: {e}")
        return False


def upsert_intraday(ticker: str, timestamp: datetime, ohlcv: Dict[str, Any]) -> bool:
    """Upsert a single intraday price record."""
    try:
        collection = get_collection("intraday")
        timestamp_iso = timestamp.isoformat()
        data = {
            "ticker": ticker,
            "timestamp": timestamp_iso,
            "open": ohlcv.get("open"),
            "high": ohlcv.get("high"),
            "low": ohlcv.get("low"),
            "close": ohlcv.get("close"),
            "volume": ohlcv.get("volume", 0),
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = collection.update_one(
            {"ticker": ticker, "timestamp": timestamp_iso},
            {
                "$set": data,
                "$setOnInsert": {"created_at": datetime.utcnow().isoformat()},
            },
            upsert=True,
        )
        return result.matched_count > 0 or result.upserted_id is not None
    except Exception as e:
        logger.error(f"Error upserting intraday: {e}")
        return False


def upsert_news(news_record: Dict[str, Any]) -> bool:
    """Upsert a single news record."""
    try:
        collection = get_collection("news")
        url = news_record.get("url")

        data = {
            "ticker": news_record.get("ticker"),
            "headline": news_record.get("headline"),
            "source": news_record.get("source"),
            "url": url,
            "published_at": news_record.get("published_at"),
            "sentiment_score": news_record.get("sentiment_score"),
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = collection.update_one(
            {"url": url},
            {
                "$set": data,
                "$setOnInsert": {"created_at": datetime.utcnow().isoformat()},
            },
            upsert=True,
        )
        return result.matched_count > 0 or result.upserted_id is not None
    except Exception as e:
        logger.error(f"Error upserting news: {e}")
        return False


def upsert_sentiment_feature(
    ticker: str, feature_date: date, sentiment: float, news_count: int
) -> bool:
    """Upsert a sentiment feature record."""
    try:
        collection = get_collection("features_sentiment")
        data = {
            "ticker": ticker,
            "date": feature_date.isoformat(),
            "sentiment": sentiment,
            "news_count": news_count,
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = collection.update_one(
            {"ticker": ticker, "date": feature_date.isoformat()},
            {
                "$set": data,
                "$setOnInsert": {"created_at": datetime.utcnow().isoformat()},
            },
            upsert=True,
        )
        return result.matched_count > 0 or result.upserted_id is not None
    except Exception as e:
        logger.error(f"Error upserting sentiment feature: {e}")
        return False


def upsert_prediction(
    ticker: str,
    pred_date: date,
    model_name: str,
    predicted_close: float,
    confidence: Optional[float] = None,
) -> bool:
    """Upsert a prediction record."""
    try:
        collection = get_collection("predictions")
        data = {
            "ticker": ticker,
            "date": pred_date.isoformat(),
            "model_name": model_name,
            "predicted_close": predicted_close,
            "confidence": confidence,
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = collection.update_one(
            {"ticker": ticker, "date": pred_date.isoformat(), "model_name": model_name},
            {
                "$set": data,
                "$setOnInsert": {"created_at": datetime.utcnow().isoformat()},
            },
            upsert=True,
        )
        return result.matched_count > 0 or result.upserted_id is not None
    except Exception as e:
        logger.error(f"Error upserting prediction: {e}")
        return False


# Query functions


def get_prices(ticker: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """Get price records for a ticker within date range."""
    try:
        collection = get_collection("prices")
        results = collection.find(
            {
                "ticker": ticker,
                "date": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat(),
                },
            }
        ).sort("date", 1)
        return list(results)
    except Exception as e:
        logger.error(f"Error fetching prices: {e}")
        return []


def get_latest_price(ticker: str) -> Optional[Dict[str, Any]]:
    """Get the latest price record for a ticker."""
    try:
        collection = get_collection("prices")
        result = collection.find_one(
            {"ticker": ticker},
            sort=[("date", -1)],
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching latest price: {e}")
        return None


def get_sentiment_by_date(
    ticker: str, start_date: date, end_date: date
) -> List[Dict[str, Any]]:
    """Get sentiment features for a ticker within date range."""
    try:
        collection = get_collection("features_sentiment")
        results = collection.find(
            {
                "ticker": ticker,
                "date": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat(),
                },
            }
        ).sort("date", 1)
        return list(results)
    except Exception as e:
        logger.error(f"Error fetching sentiment: {e}")
        return []
