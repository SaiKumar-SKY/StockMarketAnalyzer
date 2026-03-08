#!/usr/bin/env python3
"""
Unit tests for technical indicators computation.
"""

import unittest
import pandas as pd
import numpy as np

from src.indicators import IndicatorCalculator


class TestIndicators(unittest.TestCase):

    def setUp(self):
        """Set up test data."""
        # Create sample OHLCV data for testing
        dates = pd.date_range("2020-01-01", periods=50, freq="D")
        np.random.seed(42)  # For reproducible results

        self.sample_data = pd.DataFrame(
            {
                "open": 100 + np.random.randn(50).cumsum(),
                "high": 105 + np.random.randn(50).cumsum(),
                "low": 95 + np.random.randn(50).cumsum(),
                "close": 100 + np.random.randn(50).cumsum(),
                "volume": np.random.randint(1000, 10000, 50),
            },
            index=dates,
        )

        # Ensure high >= close >= low, etc.
        for i in range(len(self.sample_data)):
            high = max(
                self.sample_data.iloc[i]["open"], self.sample_data.iloc[i]["close"]
            ) + abs(np.random.randn())
            low = min(
                self.sample_data.iloc[i]["open"], self.sample_data.iloc[i]["close"]
            ) - abs(np.random.randn())
            self.sample_data.iloc[i, self.sample_data.columns.get_loc("high")] = high
            self.sample_data.iloc[i, self.sample_data.columns.get_loc("low")] = low

    def test_indicator_calculator_creation(self):
        """Test IndicatorCalculator initialization."""
        calc = IndicatorCalculator("AAPL")
        self.assertEqual(calc.ticker, "AAPL")

    def test_compute_indicators(self):
        """Test that indicators are computed without errors."""
        calc = IndicatorCalculator("TEST")
        result = calc.compute_indicators(self.sample_data.copy())

        # Check that all expected columns are present
        expected_indicators = [
            "rsi_14",
            "macd",
            "macd_signal",
            "macd_diff",
            "bb_upper",
            "bb_middle",
            "bb_lower",
            "bb_percent",
            "bb_width",
            "sma_20",
            "sma_50",
            "sma_200",
            "ema_9",
            "ema_21",
            "atr_14",
            "obv",
            "stoch_k",
            "stoch_d",
        ]

        for indicator in expected_indicators:
            self.assertIn(indicator, result.columns, f"Missing indicator: {indicator}")

        # Check that original OHLCV columns are preserved
        ohlcv_cols = ["open", "high", "low", "close", "volume"]
        for col in ohlcv_cols:
            self.assertIn(col, result.columns)

    def test_handle_nans(self):
        """Test NaN handling."""
        calc = IndicatorCalculator("TEST")
        df_with_indicators = calc.compute_indicators(self.sample_data.copy())

        # Should have some NaN values initially
        has_nans = df_with_indicators.isna().any().any()
        self.assertTrue(has_nans, "Expected some NaN values in raw indicators")

        # After handling, should have no NaN in indicator columns
        df_clean = calc.handle_nans(df_with_indicators)
        indicator_cols = [
            col
            for col in df_clean.columns
            if col not in ["open", "high", "low", "close", "volume"]
        ]
        has_indicator_nans = df_clean[indicator_cols].isna().any().any()
        self.assertFalse(
            has_indicator_nans, "No NaN values should remain in indicators"
        )

    def test_rsi_calculation(self):
        """Test RSI calculation with known values."""
        # Simple test data for RSI
        simple_data = pd.DataFrame(
            {
                "close": [
                    100,
                    102,
                    101,
                    103,
                    105,
                    104,
                    106,
                    108,
                    107,
                    109,
                    111,
                    110,
                    112,
                    114,
                    113,
                    115,
                    117,
                    116,
                    118,
                    120,
                ]
                * 3,
                "high": [
                    102,
                    104,
                    103,
                    105,
                    107,
                    106,
                    108,
                    110,
                    109,
                    111,
                    113,
                    112,
                    114,
                    116,
                    115,
                    117,
                    119,
                    118,
                    120,
                    122,
                ]
                * 3,
                "low": [
                    98,
                    100,
                    99,
                    101,
                    103,
                    102,
                    104,
                    106,
                    105,
                    107,
                    109,
                    108,
                    110,
                    112,
                    111,
                    113,
                    115,
                    114,
                    116,
                    118,
                ]
                * 3,
                "open": [
                    100,
                    102,
                    101,
                    103,
                    105,
                    104,
                    106,
                    108,
                    107,
                    109,
                    111,
                    110,
                    112,
                    114,
                    113,
                    115,
                    117,
                    116,
                    118,
                    120,
                ]
                * 3,
                "volume": [1000] * 60,
            }
        )

        calc = IndicatorCalculator("TEST")
        result = calc.compute_indicators(simple_data)

        # RSI should be calculated
        self.assertIn("rsi_14", result.columns)
        # RSI should have values between 0 and 100 for most data points
        rsi_values = result["rsi_14"].dropna()
        self.assertTrue(len(rsi_values) > 0, "Should have some RSI values")
        self.assertTrue((rsi_values >= 0).all() and (rsi_values <= 100).all())

    def test_sma_calculation(self):
        """Test SMA calculation."""
        calc = IndicatorCalculator("TEST")
        result = calc.compute_indicators(self.sample_data.copy())

        # SMA_20 should be simple moving average
        sma_20 = result["sma_20"].dropna()
        self.assertEqual(len(sma_20), len(self.sample_data) - 19)  # 20-period SMA

        # Check one value manually
        manual_sma = self.sample_data["close"].iloc[:20].mean()
        self.assertAlmostEqual(result["sma_20"].iloc[19], manual_sma, places=5)

    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation."""
        calc = IndicatorCalculator("TEST")
        result = calc.compute_indicators(self.sample_data.copy())

        # Check that upper > middle > lower for non-NaN values
        bb_data = result[["bb_upper", "bb_middle", "bb_lower"]].dropna()
        self.assertTrue((bb_data["bb_upper"] > bb_data["bb_middle"]).all())
        self.assertTrue((bb_data["bb_middle"] > bb_data["bb_lower"]).all())


if __name__ == "__main__":
    unittest.main()
