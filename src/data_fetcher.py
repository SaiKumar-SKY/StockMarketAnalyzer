#!/usr/bin/env python3
"""
Data Fetcher Script

Fetches historical OHLCV data for stock tickers using yfinance.
Supports configurable tickers, date ranges, and saves to Parquet.
Includes validation, retry logic, and logging.
"""

import argparse
import logging
import os
from datetime import datetime, timedelta
from typing import List

import pandas as pd
import yfinance as yf
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("data_fetcher.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = "data/raw"
REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


class DataFetcher:
    """Handles fetching and saving stock data."""

    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    )
    def fetch_ticker_data(
        self, ticker: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """Fetch data for a single ticker with retry logic."""
        logger.info(f"Fetching data for {ticker} from {start_date} to {end_date}")
        try:
            data = yf.download(
                ticker, start=start_date, end=end_date, auto_adjust=False
            )
            if data.empty:
                raise ValueError(f"No data returned for {ticker}")
            # Flatten MultiIndex columns if present
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            return data
        except Exception as e:
            logger.error(f"Failed to fetch {ticker}: {e}")
            raise

    def validate_data(self, data: pd.DataFrame, ticker: str) -> bool:
        """Validate the fetched data."""
        if data.empty:
            logger.error(f"Data for {ticker} is empty")
            return False

        # Check for required columns
        missing_cols = set(REQUIRED_COLUMNS) - set(data.columns)
        if missing_cols:
            logger.error(f"Missing columns for {ticker}: {missing_cols}")
            return False

        # Check data types
        for col in REQUIRED_COLUMNS:
            if not pd.api.types.is_numeric_dtype(data[col]):
                logger.error(f"Column {col} for {ticker} is not numeric")
                return False

        # Check for NaN values
        if data[REQUIRED_COLUMNS].isnull().any().any():
            logger.warning(f"NaN values found in {ticker} data")

        # Check date index
        if not isinstance(data.index, pd.DatetimeIndex):
            logger.error(f"Index for {ticker} is not DatetimeIndex")
            return False

        logger.info(f"Data validation passed for {ticker}")
        return True

    def save_data(self, data: pd.DataFrame, ticker: str):
        """Save data to Parquet format."""
        ticker_dir = os.path.join(self.data_dir, ticker.lower())
        os.makedirs(ticker_dir, exist_ok=True)

        file_path = os.path.join(ticker_dir, f"{ticker}_ohlcv.parquet")
        data.to_parquet(file_path, index=True)
        logger.info(f"Saved data for {ticker} to {file_path}")

    def fetch_and_save(self, tickers: List[str], start_date: str, end_date: str):
        """Fetch and save data for multiple tickers."""
        for ticker in tickers:
            try:
                data = self.fetch_ticker_data(ticker, start_date, end_date)
                if self.validate_data(data, ticker):
                    self.save_data(data, ticker)
                    logger.info(f"Successfully processed {ticker}")
                else:
                    logger.error(f"Validation failed for {ticker}")
            except Exception as e:
                logger.error(f"Failed to process {ticker}: {e}")


def parse_date(date_str: str) -> str:
    """Parse date string or relative date."""
    if date_str.startswith("-"):
        # Relative date like -5y
        unit = date_str[-1]
        value = int(date_str[1:-1])
        if unit == "y":
            delta = timedelta(days=value * 365)
        elif unit == "m":
            delta = timedelta(days=value * 30)
        elif unit == "d":
            delta = timedelta(days=value)
        else:
            raise ValueError(f"Invalid unit {unit}")
        return (datetime.now() - delta).strftime("%Y-%m-%d")
    else:
        return date_str


def main():
    parser = argparse.ArgumentParser(description="Fetch historical stock data")
    parser.add_argument(
        "--tickers", nargs="+", required=True, help="List of stock tickers"
    )
    parser.add_argument(
        "--start",
        type=str,
        default="-5y",
        help="Start date (YYYY-MM-DD or -Ny/-Nm/-Nd)",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date (YYYY-MM-DD)",
    )

    args = parser.parse_args()

    start_date = parse_date(args.start)
    end_date = args.end

    fetcher = DataFetcher()
    fetcher.fetch_and_save(args.tickers, start_date, end_date)


if __name__ == "__main__":
    main()
