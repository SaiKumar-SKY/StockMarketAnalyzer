#!/usr/bin/env python3
"""
Intraday Data Fetcher

Fetches intraday stock prices on a schedule during market hours.
Appends data to CSV files without duplicates.
"""

import argparse
import datetime
import holidays
import logging
import os
import time
from typing import List

import pandas as pd
import pytz
import yfinance as yf
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("intraday_fetcher.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = "data/realtime"
INTERVAL = "15m"
MARKET_TIMEZONE = pytz.timezone("US/Eastern")


class IntradayFetcher:
    """Handles scheduled intraday data fetching."""

    def __init__(self, tickers: List[str], delay: int = 1):
        self.tickers = tickers
        self.delay = delay  # seconds between API calls
        self.data_dir = DATA_DIR
        os.makedirs(self.data_dir, exist_ok=True)

    def is_market_open(self) -> bool:
        """Check if market is currently open."""
        now = datetime.datetime.now(MARKET_TIMEZONE)
        today = now.date()

        # Check if weekend
        if today.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False

        # Check if holiday
        holidays_us = holidays.US(years=today.year)
        if today in holidays_us:
            return False

        # Check time: 9:30 AM - 4:00 PM EST
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

        return market_open <= now <= market_close

    def get_last_timestamp(self, ticker: str) -> pd.Timestamp or None:
        """Get the last timestamp from existing CSV file."""
        file_path = self._get_file_path(ticker)
        if not os.path.exists(file_path):
            return None

        try:
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            if not df.empty:
                return df.index[-1]
        except Exception as e:
            logger.warning(f"Error reading last timestamp for {ticker}: {e}")

        return None

    def fetch_intraday_data(self, ticker: str) -> pd.DataFrame:
        """Fetch intraday data for a ticker."""
        last_ts = self.get_last_timestamp(ticker)

        if last_ts is not None:
            # Fetch from last timestamp + 1 interval
            start = last_ts + pd.Timedelta(minutes=15)
        else:
            # Fetch last trading day
            start = datetime.datetime.now(MARKET_TIMEZONE) - datetime.timedelta(days=1)

        try:
            logger.info(f"Fetching intraday data for {ticker} from {start}")
            data = yf.download(ticker, start=start, interval=INTERVAL, auto_adjust=True)

            if data.empty:
                logger.info(f"No new data for {ticker}")
                return pd.DataFrame()

            # Flatten columns if MultiIndex
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            return data

        except Exception as e:
            logger.error(f"Failed to fetch intraday data for {ticker}: {e}")
            return pd.DataFrame()

    def append_to_csv(self, ticker: str, data: pd.DataFrame):
        """Append new data to CSV without duplicates."""
        if data.empty:
            return

        file_path = self._get_file_path(ticker)
        file_exists = os.path.exists(file_path)

        # Remove duplicates based on index
        if file_exists:
            existing_df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            # Find new data not in existing
            new_data = data[~data.index.isin(existing_df.index)]
        else:
            new_data = data

        if new_data.empty:
            logger.info(f"No new data to append for {ticker}")
            return

        # Append to CSV
        new_data.to_csv(file_path, mode="a", header=not file_exists, index=True)
        logger.info(f"Appended {len(new_data)} rows to {file_path}")

    def _get_file_path(self, ticker: str) -> str:
        """Get the file path for a ticker's data."""
        today = datetime.datetime.now(MARKET_TIMEZONE).strftime("%Y-%m-%d")
        ticker_dir = os.path.join(self.data_dir, ticker.lower())
        os.makedirs(ticker_dir, exist_ok=True)
        return os.path.join(ticker_dir, f"{today}.csv")

    def fetch_all_tickers(self):
        """Fetch data for all tickers."""
        if not self.is_market_open():
            logger.info("Market is closed, skipping fetch")
            return

        for ticker in self.tickers:
            try:
                data = self.fetch_intraday_data(ticker)
                self.append_to_csv(ticker, data)
                time.sleep(self.delay)  # Rate limiting
            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")


def run_scheduled(fetcher: IntradayFetcher):
    """Run the fetcher on a schedule."""
    scheduler = BlockingScheduler(timezone=MARKET_TIMEZONE)

    # Schedule every 15 minutes during market hours
    trigger = CronTrigger(
        day_of_week="mon-fri",  # Monday to Friday
        hour="9-15",  # 9 AM to 3 PM (market closes at 4 PM, but fetch until 3:45)
        minute="*/15",  # Every 15 minutes
        timezone=MARKET_TIMEZONE,
    )

    scheduler.add_job(fetcher.fetch_all_tickers, trigger, id="intraday_fetch")
    logger.info("Scheduler started. Press Ctrl+C to exit.")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        scheduler.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Fetch intraday stock data")
    parser.add_argument(
        "--tickers", nargs="+", required=True, help="List of stock tickers"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=1,
        help="Delay in seconds between API calls (default: 1)",
    )
    parser.add_argument(
        "--manual", action="store_true", help="Run once manually instead of scheduling"
    )

    args = parser.parse_args()

    fetcher = IntradayFetcher(args.tickers, args.delay)

    if args.manual:
        logger.info("Running in manual mode")
        fetcher.fetch_all_tickers()
    else:
        run_scheduled(fetcher)


if __name__ == "__main__":
    main()
