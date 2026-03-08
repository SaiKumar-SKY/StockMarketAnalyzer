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

### Step 4: Verify Setup

Run the smoke test to ensure all modules import correctly:
```bash
python smoke_test.py
```

You should see: "All imports successful! Environment is ready."

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