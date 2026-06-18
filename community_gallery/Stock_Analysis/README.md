# Stock Analysis Dashboard - Powered by Preswald

A **fully interactive stock analysis dashboard** built using the [Preswald](https://github.com/StructuredLabs/preswald) open-source framework.  
This project allows you to visualize stock data with multiple chart types, technical indicators, and a clean, easy-to-use interface — perfect for quick stock trend analysis.

**Live Demo**: [Stock Analysis Dashboard](https://stock-analysis-362749-xrircnfp.preswald.app/)

---

## Features
- Interactive **Line Chart** and **Candlestick Chart**
- Multiple timeframe selection: `1 Week`, `1 Month`, `1 Year`, `5 Years`
- Technical Indicators:
  - **Simple Moving Average (SMA)**
  - **Exponential Moving Average (EMA)**
  - **Relative Strength Index (RSI)**
  - **Bollinger Bands**
- Auto-generated bullish/bearish signal based on indicator analysis
- Summary stats: Lowest Price, Highest Price, and Average Close Price
- Filterable stock data table for detailed analysis

---

## Data Source

Stock data used in this project is based on Google stock data fetched from Yahoo Finance for demonstration purposes.
Reference: [Yahoo Finance - Alphabet Inc. (GOOG)](https://finance.yahoo.com/quote/GOOG/history/)

---

## Installation & Running the Project

### Install **Preswald**
```bash
pip install preswald
```
### Create a folder and add `clone.sh` in it. Then copy the given code into it.

```sh
FOLDER="community_gallery/Stock_Analysis"
REPO_URL="https://github.com/StructuredLabs/preswald.git"

# Initialize a bare repository without downloading files
git clone --no-checkout $REPO_URL temp-repo

# Navigate to the temporary repository
cd temp-repo

# Enable sparse checkout
git sparse-checkout init --cone

# Set the specific folder to checkout
git sparse-checkout set $FOLDER

# Pull only the files in the specified folder
git checkout

# Move the contents of the specified folder to the current directory
mv $FOLDER/* ../

# Go back to the parent directory and clean up
cd ..
rm -rf temp-repo
```

### Clone the Project by running the script
```bash
bash clone.sh
```

### Run the App
```bash
preswald run
```

View the dashboard at: http://localhost:8501
That’s it! Your interactive stock dashboard will be up and running. 