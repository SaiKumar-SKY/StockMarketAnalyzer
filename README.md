# Stock Market Analyzer

A Python project for stock market analysis with data processing, visualization, and machine learning capabilities.

## Environment Setup

This guide helps you set up a reproducible Python environment from scratch using free and open-source tools.

### Prerequisites

- Windows, macOS, or Linux operating system
- Internet connection for downloading Python and packages

### Step 1: Install Python 3.10+

1. Download Python 3.10 or later from the official website: https://www.python.org/downloads/
2. Run the installer and ensure "Add Python to PATH" is checked
3. Verify installation by opening a terminal and running:
   ```bash
   python --version
   ```
   You should see Python 3.10.x or higher.

### Step 2: Set Up Virtual Environment

1. Navigate to the project directory in your terminal
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

### Step 3: Install Dependencies

With the virtual environment activated, install all required packages:
```bash
pip install -r requirements.txt
```

This will install:
- pandas: Data manipulation and analysis
- numpy: Numerical computing
- scikit-learn: Machine learning
- yfinance: Yahoo Finance data
- ta: Technical analysis
- matplotlib: Plotting
- plotly: Interactive visualizations
- streamlit: Web app framework
- joblib: Parallel computing
- pymongo: MongoDB driver
- pydantic: Data validation

### Step 4: Set Up MongoDB

This project uses MongoDB as the primary database. Ensure MongoDB is installed and running:

**Windows:**
- Download from https://www.mongodb.com/try/download/community
- Follow the installation guide
- MongoDB runs as a service on `localhost:27017` by default

**macOS (using Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
```

**Verify MongoDB is running:**
```bash
mongo --eval "db.adminCommand('ping')"
```

### Step 5: Initialize Database

Initialize MongoDB collections and indexes:
```bash
python scripts/init_db.py
```

This creates:
- `prices`: Daily OHLCV data with unique (ticker, date) constraint
- `intraday`: 15-minute interval data with unique (ticker, timestamp) constraint
- `news`: Financial news with unique URL constraint
- `features_sentiment`: Daily sentiment aggregates
- `predictions`: Model predictions and backtests

### Step 6: Verify Setup

Run the smoke test to ensure all modules import correctly:
```bash
python smoke_test.py
```

Run database tests:
```bash
python -m pytest tests/test_database.py -v
```

### Deactivating the Environment

When done working, deactivate the virtual environment:
```bash
deactivate
```

## Data Fetching

The project includes a data fetcher script to download historical OHLCV stock data.

### Usage

Activate the virtual environment and run:

```bash
python src/data_fetcher.py --tickers AAPL MSFT GOOGL --start -5y
```

### Options

- `--tickers`: List of stock tickers (required)
- `--start`: Start date (YYYY-MM-DD or relative like -5y, -6m, -30d) (default: -5y)
- `--end`: End date (YYYY-MM-DD) (default: today)

### Features

- Fetches data using yfinance (free, no rate limits)
- Validates data integrity (no missing columns, numeric types, date index)
- Saves to Parquet format under `/data/raw/{ticker}/`
- Includes retry logic with exponential backoff for network issues
- Logs all operations to `data_fetcher.log`

### Example

```bash
python src/data_fetcher.py --tickers TSLA NVDA --start 2020-01-01 --end 2023-12-31
```

This will download 4 years of data for TSLA and NVDA, validate it, and save to partitioned Parquet files.

## Intraday Data Fetching

The project includes a scheduled intraday data fetcher for real-time stock prices during market hours.

### Usage

To run the scheduler manually for testing:

```bash
python src/intraday_fetcher.py --tickers AAPL MSFT --mode manual
```

To start the background scheduler:

```bash
python src/intraday_fetcher.py --tickers AAPL MSFT
```

### Options

- `--tickers`: List of stock tickers (required)
- `--mode`: 'scheduled' (default) or 'manual' for one-time fetch

### Features

- Fetches 15-minute interval data during market hours (9:30 AM - 4:00 PM EST)
- Respects US market holidays and weekends
- Appends new data to CSV files under `/data/realtime/{ticker}/` without duplicates
- Uses APScheduler for reliable background scheduling
- Includes rate limiting and API error handling
- Logs all operations to `intraday_fetcher.log`

### Scheduled Mode

In scheduled mode, the script runs continuously and fetches data every 15 minutes during market hours. It automatically stops outside market hours and resumes the next trading day.

### Manual Mode

In manual mode, performs one fetch operation regardless of market hours, useful for testing or backfilling.

### Example

```bash
python src/intraday_fetcher.py --tickers GOOGL AMZN --mode manual
```

This will fetch the latest 15-minute data for GOOGL and AMZN and append to their CSV files.

## News Headline Fetching

The project includes a news fetcher to collect financial news headlines for sentiment analysis.

### Usage

To fetch news headlines and compute sentiment:

```bash
python src/news_fetcher.py --tickers AAPL MSFT GOOGL
```

### Options

- `--tickers`: List of stock tickers (required)
- `--date`: Target date in YYYY-MM-DD format (default: today)

### Features

- Fetches recent news headlines using yfinance (free, no API key required)
- Performs VADER sentiment analysis on each headline (compound score -1 to +1)
- De-duplicates headlines by URL hash
- Saves detailed news data to `/data/news/news_{date}.csv`
- Aggregates daily average sentiment per ticker to `/data/features/sentiment/sentiment_{date}.csv`
- Handles tickers with no news gracefully (outputs NaN for sentiment)

### Output Format

News CSV columns: `ticker`, `headline`, `source`, `published_at`, `url`, `sentiment_score`

Sentiment CSV columns: `ticker`, `sentiment` (average compound score)

### Example

```bash
python src/news_fetcher.py --tickers TSLA NVDA --date 2026-03-08
```

This will fetch news for TSLA and NVDA, analyze sentiment, and save to dated CSV files.

## Technical Indicators

The project computes standard technical analysis indicators from OHLCV data for machine learning feature engineering.

### Usage

To compute indicators for a stock ticker:

```bash
python scripts/compute_indicators.py AAPL
```

### Options

- `ticker`: Stock ticker symbol (required)
- `--start-date`: Start date (YYYY-MM-DD) (default: 5 years ago)
- `--end-date`: End date (YYYY-MM-DD) (default: today)

### Computed Indicators

The following indicators are calculated using the `ta` library:

- **RSI (14)**: Relative Strength Index
- **MACD (12/26/9)**: Moving Average Convergence Divergence with signal line
- **Bollinger Bands (20/2)**: Upper, middle, lower bands with %B and bandwidth
- **SMA (20, 50, 200)**: Simple Moving Averages
- **EMA (9, 21)**: Exponential Moving Averages
- **ATR (14)**: Average True Range
- **OBV**: On-Balance Volume
- **Stochastic Oscillator (14/3/3)**: %K and %D lines

### Features

- Fetches OHLCV data from MongoDB `prices` collection
- Computes all indicators using vectorized operations for performance
- Handles NaN values by dropping rows with incomplete indicator data (warmup periods)
- Saves clean indicator data to `/data/features/{ticker}_indicators.parquet`
- Modular design allows easy addition of new indicators
- Unit tests verify calculation accuracy against known reference values
- Processes 5 years of daily data in under 30 seconds

### Output Format

Parquet file contains OHLCV columns plus all indicator columns, indexed by date.

### Example

```bash
python scripts/compute_indicators.py MSFT --start-date 2020-01-01 --end-date 2023-12-31
```

This computes indicators for MSFT using 4 years of data and saves to `data/features/msft_indicators.parquet`.

## Database Architecture

All ingested data is persisted in MongoDB using Pydantic models for validation. The database automatically handles upsert operations to prevent duplicates.

### Collections

The project uses 5 MongoDB collections:

#### prices
- **Schema**: `{ticker, date, open, high, low, close, volume, created_at, updated_at}`
- **Index**: Unique compound index on `(ticker, date)`
- **Purpose**: Daily OHLCV data
- **Query**: `db.prices.find({ticker: "AAPL"}).sort({date: -1})`

#### intraday
- **Schema**: `{ticker, timestamp, open, high, low, close, volume, created_at, updated_at}`
- **Index**: Unique compound index on `(ticker, timestamp)`
- **Purpose**: 15-minute interval price data
- **Query**: `db.intraday.find({ticker: "AAPL"}).sort({timestamp: -1})`

#### news
- **Schema**: `{url, ticker, headline, source, published_at, sentiment_score, created_at, updated_at}`
- **Index**: Unique index on `url`
- **Purpose**: Financial news headlines with VADER sentiment
- **Query**: `db.news.find({ticker: "AAPL"}).sort({published_at: -1})`

#### features_sentiment
- **Schema**: `{ticker, date, sentiment, news_count, created_at, updated_at}`
- **Index**: Unique compound index on `(ticker, date)`
- **Purpose**: Daily aggregated sentiment features
- **Query**: `db.features_sentiment.find({ticker: "AAPL"}).sort({date: -1})`

#### predictions
- **Schema**: `{ticker, date, model_name, predicted_close, confidence, created_at, updated_at}`
- **Index**: Unique compound index on `(ticker, date, model_name)`
- **Purpose**: Model predictions and backtest results
- **Query**: `db.predictions.find({ticker: "AAPL", model_name: "xgboost"})`

### Database Operations

All database operations are in `src/db_operations.py`:

```python
from src.db_operations import (
    upsert_price,
    upsert_intraday,
    upsert_news,
    upsert_sentiment_feature,
    upsert_prediction,
    get_prices,
    get_latest_price,
    get_sentiment_by_date,
)

# Upsert price (idempotent operation)
upsert_price("AAPL", date(2023, 1, 1), {
    "open": 150.0,
    "high": 155.0,
    "low": 149.0,
    "close": 152.5,
    "volume": 1000000,
})

# Query prices for date range
prices = get_prices("AAPL", date(2023, 1, 1), date(2023, 12, 31))

# Get latest price
latest = get_latest_price("AAPL")

# Get sentiment for date range
sentiment = get_sentiment_by_date("AAPL", date(2023, 1, 1), date(2023, 12, 31))
```

### Upsert Pattern

All upsert operations use MongoDB's atomic `update_one` with `upsert=True`:

```python
collection.update_one(
    filter={"ticker": ticker, "date": date_str},
    update={
        "$set": data_dict,
        "$setOnInsert": {"created_at": datetime.utcnow().isoformat()},
    },
    upsert=True,
)
```

This ensures:
- **Idempotency**: Running the same upsert twice produces the same state
- **No Duplicates**: Unique indexes prevent duplicate records
- **Performance**: Sub-500ms queries on indexed fields

The project includes a fully local interactive notebook environment. Follow these steps after activating the virtual environment:

1. Ensure dependencies are installed (the `requirements.txt` now contains Jupyter-related packages):
   ```bash
   pip install -r requirements.txt
   ```
2. Launch JupyterLab:
   ```bash
   jupyter lab
   ```
   A browser window should open showing the interface. All notebooks in `/notebooks/` will be accessible.
3. The kernel used by notebooks will correspond to the project's virtual environment; you can verify by running the following in a cell:
   ```python
   import sys
   print(sys.executable)
   ```
   It should point to `.../venv/...`.
4. A sample exploratory notebook (`/notebooks/01_data_exploration.ipynb`) is included; it loads stock data and renders interactive Plotly charts. Open it to confirm everything works.

### Kernel & Hardware Upgrades

If you later acquire a remote machine or GPU, you can connect to a remote kernel from JupyterLab. Install `jupyter-client` on the remote host and start a kernel there, then follow [Jupyter documentation](https://jupyter.readthedocs.io/) to configure `jupyter_client.connect` file or use `ssh -L` tunneling. This allows you to run heavy computations on external hardware while editing locally.

### Notebook Version Control

All notebooks live under `/notebooks/` and are tracked by Git. The pre-commit configuration includes `nbstripout`, which automatically strips output from notebooks before commits to keep the repository clean. To enable it manually, run:

```bash
nbstripout --install
```

Outputs will be removed each time you commit changes to `.ipynb` files.

### Extensions

The following JupyterLab extensions are installed in the environment:
- `jupyterlab-git` for repository integration
- `jupyter-resource-usage` to display local RAM/CPU usage
- `jupyterlab-lsp` for language server support

You can install additional extensions via `pip` and enable them with `jupyter labextension install` if needed.

### Checking GPU Availability

Notebooks include a small cell that will report whether a local CUDA-capable GPU is detected. This is informational and does not change any configuration. Example code:

```python
import torch
print('CUDA available:', torch.cuda.is_available())
```