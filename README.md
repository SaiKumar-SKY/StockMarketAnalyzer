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

### Reproducing on Another Machine

Repeat steps 1-4 on any machine to get the exact same environment.

## Usage

Once set up, you can start building your stock analysis pipeline using the installed libraries.