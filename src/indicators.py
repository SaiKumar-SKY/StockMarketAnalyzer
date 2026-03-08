#!/usr/bin/env python3
"""
Technical analysis indicators computation module.
Computes various indicators from OHLCV data and saves to parquet files.
"""

import logging
import pandas as pd
from datetime import date, timedelta
from typing import Optional
from pathlib import Path

from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

from src.db_operations import get_prices

logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """Computes technical analysis indicators from OHLCV data."""

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()

    def fetch_data(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """Fetch OHLCV data from database."""
        if start_date is None:
            start_date = date.today() - timedelta(days=365 * 5)  # 5 years
        if end_date is None:
            end_date = date.today()

        prices = get_prices(self.ticker, start_date, end_date)
        if not prices:
            logger.warning(f"No price data found for {self.ticker}")
            return pd.DataFrame()

        df = pd.DataFrame(prices)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").set_index("date")
        return df[["open", "high", "low", "close", "volume"]]

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute all technical indicators."""
        if df.empty:
            return df

        # RSI (14)
        rsi = RSIIndicator(close=df["close"], window=14)
        df["rsi_14"] = rsi.rsi()

        # MACD (12/26/9)
        macd = MACD(close=df["close"], window_slow=26, window_fast=12, window_sign=9)
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()
        df["macd_diff"] = macd.macd_diff()

        # Bollinger Bands (20/2)
        bb = BollingerBands(close=df["close"], window=20, window_dev=2)
        df["bb_upper"] = bb.bollinger_hband()
        df["bb_middle"] = bb.bollinger_mavg()
        df["bb_lower"] = bb.bollinger_lband()
        df["bb_percent"] = bb.bollinger_pband()
        df["bb_width"] = bb.bollinger_wband()

        # SMA (20, 50, 200)
        sma_20 = SMAIndicator(close=df["close"], window=20)
        df["sma_20"] = sma_20.sma_indicator()

        sma_50 = SMAIndicator(close=df["close"], window=50)
        df["sma_50"] = sma_50.sma_indicator()

        sma_200 = SMAIndicator(close=df["close"], window=200)
        df["sma_200"] = sma_200.sma_indicator()

        # EMA (9, 21)
        ema_9 = EMAIndicator(close=df["close"], window=9)
        df["ema_9"] = ema_9.ema_indicator()

        ema_21 = EMAIndicator(close=df["close"], window=21)
        df["ema_21"] = ema_21.ema_indicator()

        # ATR (14)
        atr = AverageTrueRange(
            high=df["high"], low=df["low"], close=df["close"], window=14
        )
        df["atr_14"] = atr.average_true_range()

        # OBV
        obv = OnBalanceVolumeIndicator(close=df["close"], volume=df["volume"])
        df["obv"] = obv.on_balance_volume()

        # Stochastic Oscillator (14, 3, 3)
        stoch = StochasticOscillator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=14,
            smooth_window=3,
        )
        df["stoch_k"] = stoch.stoch()
        df["stoch_d"] = stoch.stoch_signal()

        return df

    def handle_nans(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle NaN values from indicator warmup periods."""
        # Drop rows where any indicator is NaN
        indicator_cols = [
            col
            for col in df.columns
            if col not in ["open", "high", "low", "close", "volume"]
        ]
        df_clean = df.dropna(subset=indicator_cols)
        logger.info(
            f"Dropped {len(df) - len(df_clean)} rows with NaN indicators for {self.ticker}"
        )
        return df_clean

    def save_to_parquet(
        self, df: pd.DataFrame, output_dir: str = "data/features"
    ) -> bool:
        """Save indicators to parquet file."""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            file_path = output_path / f"{self.ticker.lower()}_indicators.parquet"
            df.to_parquet(file_path)
            logger.info(f"Saved indicators for {self.ticker} to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving parquet: {e}")
            return False

    def compute_and_save(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> bool:
        """Compute indicators and save to file."""
        df = self.fetch_data(start_date, end_date)
        if df.empty:
            return False

        df_with_indicators = self.compute_indicators(df)
        df_clean = self.handle_nans(df_with_indicators)
        return self.save_to_parquet(df_clean)


def compute_indicators_for_ticker(
    ticker: str, start_date: Optional[date] = None, end_date: Optional[date] = None
) -> bool:
    """Convenience function to compute indicators for a ticker."""
    calculator = IndicatorCalculator(ticker)
    return calculator.compute_and_save(start_date, end_date)
