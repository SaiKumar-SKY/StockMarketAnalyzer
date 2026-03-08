#!/usr/bin/env python3
"""
Unit tests for intraday_fetcher.py
"""

import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch
import pandas as pd
import pytz

from src.intraday_fetcher import IntradayFetcher


class TestIntradayFetcher(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.fetcher = IntradayFetcher(["AAPL"], delay=0)
        self.fetcher.data_dir = self.temp_dir

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_is_market_open_weekday_during_hours(self):
        """Test market open detection during weekday hours."""
        # Mock to 10 AM EST on Tuesday 2023-01-03 (not holiday)
        mock_now = datetime(
            2023,
            1,
            3,
            10,
            0,
            tzinfo=pytz.timezone("US/Eastern"),
        )

        with patch("src.intraday_fetcher.datetime.datetime") as mock_datetime_class:
            mock_datetime_class.now.return_value = mock_now
            self.assertTrue(self.fetcher.is_market_open())

    def test_is_market_open_weekend(self):
        """Test market closed on weekend."""
        mock_now = datetime(
            2023, 1, 7, 10, 0, tzinfo=pytz.timezone("US/Eastern")
        )  # Saturday

        with patch("src.intraday_fetcher.datetime.datetime") as mock_datetime_class:
            mock_datetime_class.now.return_value = mock_now
            self.assertFalse(self.fetcher.is_market_open())

    def test_is_market_open_before_hours(self):
        """Test market closed before opening."""
        mock_now = datetime(
            2023, 1, 3, 8, 0, tzinfo=pytz.timezone("US/Eastern")
        )  # Tuesday 8 AM

        with patch("src.intraday_fetcher.datetime.datetime") as mock_datetime_class:
            mock_datetime_class.now.return_value = mock_now
            self.assertFalse(self.fetcher.is_market_open())

    def test_is_market_open_after_hours(self):
        """Test market closed after closing."""
        mock_now = datetime(
            2023, 1, 3, 17, 0, tzinfo=pytz.timezone("US/Eastern")
        )  # Tuesday 5 PM

        with patch("src.intraday_fetcher.datetime.datetime") as mock_datetime_class:
            mock_datetime_class.now.return_value = mock_now
            self.assertFalse(self.fetcher.is_market_open())

    @patch("src.intraday_fetcher.yf.download")
    def test_fetch_intraday_data_success(self, mock_download):
        """Test successful intraday data fetch."""
        mock_data = pd.DataFrame(
            {
                "Open": [100, 101],
                "High": [105, 106],
                "Low": [99, 100],
                "Close": [104, 105],
                "Volume": [1000, 1100],
            },
            index=pd.date_range("2023-01-01 09:30:00", periods=2, freq="15min"),
        )

        mock_download.return_value = mock_data

        result = self.fetcher.fetch_intraday_data("AAPL")
        pd.testing.assert_frame_equal(result, mock_data)

    @patch("src.intraday_fetcher.yf.download")
    def test_fetch_intraday_data_empty(self, mock_download):
        """Test fetch with no new data."""
        mock_download.return_value = pd.DataFrame()

        result = self.fetcher.fetch_intraday_data("AAPL")
        self.assertTrue(result.empty)

    def test_append_to_csv_new_file(self):
        """Test appending to new CSV file."""
        data = pd.DataFrame(
            {
                "Open": [100],
                "High": [105],
                "Low": [99],
                "Close": [104],
                "Volume": [1000],
            },
            index=pd.date_range("2023-01-01 09:30:00", periods=1, freq="15min"),
        )

        self.fetcher.append_to_csv("AAPL", data)

        file_path = self.fetcher._get_file_path("AAPL")
        self.assertTrue(os.path.exists(file_path))

        loaded = pd.read_csv(file_path, index_col=0, parse_dates=True)
        pd.testing.assert_frame_equal(loaded, data, check_freq=False)

    def test_append_to_csv_no_duplicates(self):
        """Test appending without creating duplicates."""
        data1 = pd.DataFrame(
            {
                "Open": [100],
                "High": [105],
                "Low": [99],
                "Close": [104],
                "Volume": [1000],
            },
            index=pd.date_range("2023-01-01 09:30:00", periods=1, freq="15min"),
        )

        data2 = pd.DataFrame(
            {
                "Open": [101],
                "High": [106],
                "Low": [100],
                "Close": [105],
                "Volume": [1100],
            },
            index=pd.date_range("2023-01-01 09:45:00", periods=1, freq="15min"),
        )

        self.fetcher.append_to_csv("AAPL", data1)
        self.fetcher.append_to_csv("AAPL", data1)  # Duplicate
        self.fetcher.append_to_csv("AAPL", data2)  # New

        file_path = self.fetcher._get_file_path("AAPL")
        loaded = pd.read_csv(file_path, index_col=0, parse_dates=True)

        # Should have 2 rows: original + new
        self.assertEqual(len(loaded), 2)


if __name__ == "__main__":
    unittest.main()
