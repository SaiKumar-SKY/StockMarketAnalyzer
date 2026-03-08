#!/usr/bin/env python3
"""
Smoke test script to verify all required modules can be imported.
"""

try:
    import pandas
    import numpy
    import sklearn
    import yfinance
    import ta
    import matplotlib
    import plotly
    import streamlit
    import joblib
    print("All imports successful! Environment is ready.")
except ImportError as e:
    print(f"Import error: {e}")
    exit(1)