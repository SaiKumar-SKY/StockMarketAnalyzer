#!/usr/bin/env python3
"""
Database module with MongoDB for stock market data.
"""

from datetime import datetime, date
from typing import Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pydantic import BaseModel, Field, ConfigDict

# MongoDB configuration
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "stock_market"

# Initialize MongoDB client
client = MongoClient(MONGO_URL)
db = client[DB_NAME]


class PriceModel(BaseModel):
    """Historical daily OHLCV price data."""

    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }
    )


class IntradayPriceModel(BaseModel):
    """Intraday 15-minute interval price data."""

    ticker: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )


class NewsModel(BaseModel):
    """Financial news headlines with sentiment scores."""

    url: str
    ticker: str
    headline: str
    source: str
    published_at: int
    sentiment_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )


class SentimentFeatureModel(BaseModel):
    """Daily aggregated sentiment features per ticker."""

    ticker: str
    date: date
    sentiment: Optional[float] = None
    news_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }
    )


class PredictionModel(BaseModel):
    """Model predictions for stock prices."""

    ticker: str
    date: date
    model_name: str
    predicted_close: float
    confidence: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }
    )


def get_collection(collection_name: str):
    """Get a MongoDB collection."""
    return db[collection_name]


def init_db():
    """Initialize database and create collections with indexes."""
    try:
        # Create collections if they don't exist
        collections = [
            "prices",
            "intraday",
            "news",
            "features_sentiment",
            "predictions",
        ]

        for col_name in collections:
            if col_name not in db.list_collection_names():
                db.create_collection(col_name)
                print(f"Created collection: {col_name}")
            else:
                print(f"Collection exists: {col_name}")

        # Create indexes for prices collection
        prices_col = get_collection("prices")
        prices_col.create_index(
            [("ticker", ASCENDING), ("date", ASCENDING)], unique=True
        )
        prices_col.create_index([("ticker", ASCENDING)])
        prices_col.create_index([("date", ASCENDING)])
        print("Created indexes for prices collection")

        # Create indexes for intraday collection
        intraday_col = get_collection("intraday")
        intraday_col.create_index(
            [("ticker", ASCENDING), ("timestamp", ASCENDING)], unique=True
        )
        intraday_col.create_index([("ticker", ASCENDING)])
        intraday_col.create_index([("timestamp", DESCENDING)])
        print("Created indexes for intraday collection")

        # Create indexes for news collection
        news_col = get_collection("news")
        news_col.create_index([("url", ASCENDING)], unique=True)
        news_col.create_index([("ticker", ASCENDING)])
        news_col.create_index([("published_at", DESCENDING)])
        print("Created indexes for news collection")

        # Create indexes for sentiment collection
        sentiment_col = get_collection("features_sentiment")
        sentiment_col.create_index(
            [("ticker", ASCENDING), ("date", ASCENDING)], unique=True
        )
        sentiment_col.create_index([("ticker", ASCENDING)])
        sentiment_col.create_index([("date", DESCENDING)])
        print("Created indexes for sentiment collection")

        # Create indexes for predictions collection
        predictions_col = get_collection("predictions")
        predictions_col.create_index(
            [("ticker", ASCENDING), ("date", ASCENDING), ("model_name", ASCENDING)],
            unique=True,
        )
        predictions_col.create_index([("ticker", ASCENDING)])
        predictions_col.create_index([("date", DESCENDING)])
        print("Created indexes for predictions collection")

        print(f"Database initialized: {DB_NAME}")
        return db

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
