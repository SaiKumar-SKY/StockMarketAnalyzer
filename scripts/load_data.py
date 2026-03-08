#!/usr/bin/env python3
"""
Script to load historical OHLCV data from parquet files into MongoDB.
"""

import argparse
import logging
import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db_operations import upsert_price  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_ticker_data(ticker: str, parquet_path: str) -> bool:
    """Load data for a ticker from parquet file into MongoDB."""
    try:
        df = pd.read_parquet(parquet_path)
        logger.info(f"Loaded {len(df)} rows for {ticker}")

        success_count = 0
        for date, row in df.iterrows():
            ohlcv = {
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
            }

            # Convert date to date object
            if isinstance(date, str):
                date_obj = datetime.fromisoformat(date).date()
            else:
                date_obj = date.date()

            success = upsert_price(ticker, date_obj, ohlcv)
            if success:
                success_count += 1

        logger.info(
            f"Successfully loaded {success_count}/{len(df)} records for {ticker}"
        )
        return success_count == len(df)

    except Exception as e:
        logger.error(f"Error loading data for {ticker}: {e}")
        return False


def load_all_data(data_dir: str = "data/raw") -> None:
    """Load all parquet files in the data directory."""
    data_path = Path(data_dir)
    if not data_path.exists():
        logger.error(f"Data directory {data_dir} does not exist")
        return

    parquet_files = list(data_path.glob("**/*.parquet"))
    logger.info(f"Found {len(parquet_files)} parquet files")

    for parquet_file in parquet_files:
        # Extract ticker from filename (e.g., AAPL_ohlcv.parquet -> AAPL)
        ticker = parquet_file.stem.split("_")[0].upper()
        logger.info(f"Loading data for {ticker} from {parquet_file}")
        load_ticker_data(ticker, str(parquet_file))


def main():
    parser = argparse.ArgumentParser(description="Load historical data into MongoDB")
    parser.add_argument("--ticker", help="Specific ticker to load")
    parser.add_argument("--file", help="Specific parquet file to load")
    parser.add_argument("--all", action="store_true", help="Load all parquet files")

    args = parser.parse_args()

    if args.all:
        load_all_data()
    elif args.ticker and args.file:
        load_ticker_data(args.ticker, args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
