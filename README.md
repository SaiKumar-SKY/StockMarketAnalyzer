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

## JupyterLab Local Environment

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