#!/usr/bin/env python3
"""
Smoke test script to verify all required modules can be imported.
"""

try:
    import pandas  # noqa: F401
    import numpy  # noqa: F401
    import sklearn  # noqa: F401
    import yfinance  # noqa: F401
    import ta  # noqa: F401
    import matplotlib  # noqa: F401
    import plotly  # noqa: F401
    import streamlit  # noqa: F401
    import joblib  # noqa: F401

    print("All imports successful! Environment is ready.")
except ImportError as e:
    print(f"Import error: {e}")
    exit(1)
