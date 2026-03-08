#!/usr/bin/env python3
"""
Unit tests for data_fetcher.py
"""

import os
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd

from src.data_fetcher import DataFetcher


class TestDataFetcher(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.fetcher = DataFetcher(self.temp_dir)

    def tearDown(self):
        # Clean up temp files
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_validate_data_valid(self):
        """Test validation with valid data."""
        data = pd.DataFrame(
            {
                "Open": [100, 101],
                "High": [105, 106],
                "Low": [99, 100],
                "Close": [104, 105],
                "Volume": [1000, 1100],
            },
            index=pd.date_range("2023-01-01", periods=2),
        )

        self.assertTrue(self.fetcher.validate_data(data, "TEST"))

    def test_validate_data_empty(self):
        """Test validation with empty data."""
        data = pd.DataFrame()
        self.assertFalse(self.fetcher.validate_data(data, "TEST"))

    def test_validate_data_missing_columns(self):
        """Test validation with missing columns."""
        data = pd.DataFrame(
            {
                "Open": [100],
                "High": [105],
                # Missing Low, Close, Volume
            },
            index=pd.date_range("2023-01-01", periods=1),
        )

        self.assertFalse(self.fetcher.validate_data(data, "TEST"))

    def test_validate_data_non_numeric(self):
        """Test validation with non-numeric columns."""
        data = pd.DataFrame(
            {
                "Open": ["a"],
                "High": [105],
                "Low": [99],
                "Close": [104],
                "Volume": [1000],
            },
            index=pd.date_range("2023-01-01", periods=1),
        )

        self.assertFalse(self.fetcher.validate_data(data, "TEST"))

    def test_validate_data_wrong_index(self):
        """Test validation with non-datetime index."""
        data = pd.DataFrame(
            {
                "Open": [100],
                "High": [105],
                "Low": [99],
                "Close": [104],
                "Volume": [1000],
            },
            index=[0],
        )

        self.assertFalse(self.fetcher.validate_data(data, "TEST"))

    @patch("src.data_fetcher.yf.download")
    def test_fetch_ticker_data_success(self, mock_download):
        """Test successful data fetch."""
        mock_data = pd.DataFrame(
            {
                "Open": [100],
                "High": [105],
                "Low": [99],
                "Close": [104],
                "Volume": [1000],
            },
            index=pd.date_range("2023-01-01", periods=1),
        )

        mock_download.return_value = mock_data

        result = self.fetcher.fetch_ticker_data("AAPL", "2023-01-01", "2023-01-02")
        pd.testing.assert_frame_equal(result, mock_data)

    @patch("src.data_fetcher.yf.download")
    def test_fetch_ticker_data_empty(self, mock_download):
        """Test fetch with empty data."""
        mock_download.return_value = pd.DataFrame()

        with self.assertRaises(ValueError):
            self.fetcher.fetch_ticker_data("INVALID", "2023-01-01", "2023-01-02")

    @patch("src.data_fetcher.yf.download")
    def test_fetch_ticker_data_retry(self, mock_download):
        """Test retry logic on failure."""
        mock_download.side_effect = [
            ConnectionError,
            pd.DataFrame(
                {
                    "Open": [100],
                    "High": [105],
                    "Low": [99],
                    "Close": [104],
                    "Volume": [1000],
                },
                index=pd.date_range("2023-01-01", periods=1),
            ),
        ]

        result = self.fetcher.fetch_ticker_data("AAPL", "2023-01-01", "2023-01-02")
        self.assertEqual(len(result), 1)

    def test_save_data(self):
        """Test saving data to Parquet."""
        data = pd.DataFrame(
            {
                "Open": [100],
                "High": [105],
                "Low": [99],
                "Close": [104],
                "Volume": [1000],
            },
            index=pd.date_range("2023-01-01", periods=1),
        )

        self.fetcher.save_data(data, "TEST")

        file_path = os.path.join(self.temp_dir, "test", "TEST_ohlcv.parquet")
        self.assertTrue(os.path.exists(file_path))

        # Load and verify
        loaded = pd.read_parquet(file_path)
        pd.testing.assert_frame_equal(loaded, data, check_freq=False)


if __name__ == "__main__":
    unittest.main()
