# Cryptocurrency Market Analysis Example

This example demonstrates how to create an interactive cryptocurrency market analysis dashboard using Preswald.

## 📌 Dataset Source

- Data Source: [CoinGecko API](https://www.coingecko.com/api)
- Sample Data: [`coins.csv`](./data/coins.csv)

## 🚀 What the App Does

This Preswald app visualizes cryptocurrency market data, enabling you to:

- Sort cryptocurrencies by various metrics (e.g., Market Cap, Price).
- Filter cryptocurrencies by Market Cap threshold.
- View interactive scatter plots, bar charts, and line charts showing trends, rankings, and price movements.

## 🛠️ How to Run the App Locally

1. Clone the repository and navigate to the example folder:

```bash
git clone https://github.com/preswald/preswald.git
cd preswald/community_gallery/crypto_market_analysis

python -m venv preswald_env
source preswald_env/bin/activate

pip install preswald pandas plotly requests

preswald run

