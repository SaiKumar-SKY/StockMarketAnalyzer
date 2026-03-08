#!/usr/bin/env python3
"""
Script to compute technical analysis indicators for stock tickers.
"""

import argparse
import logging
import sys
import os
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.indicators import compute_indicators_for_ticker  # noqa: E402

logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(
        description="Compute technical indicators for stocks"
    )
    parser.add_argument("ticker", help="Stock ticker symbol")
    parser.add_argument(
        "--start-date", type=str, help="Start date (YYYY-MM-DD)", default=None
    )
    parser.add_argument(
        "--end-date", type=str, help="End date (YYYY-MM-DD)", default=None
    )

    args = parser.parse_args()

    start_date = date.fromisoformat(args.start_date) if args.start_date else None
    end_date = date.fromisoformat(args.end_date) if args.end_date else None

    success = compute_indicators_for_ticker(args.ticker, start_date, end_date)
    if success:
        print(f"Successfully computed indicators for {args.ticker}")
    else:
        print(f"Failed to compute indicators for {args.ticker}")
        exit(1)


if __name__ == "__main__":
    main()
