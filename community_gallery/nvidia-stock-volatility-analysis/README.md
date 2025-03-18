
# NVIDIA Stock Volatility Analysis App
## Dataset Source
The dataset used in this application is sourced from publicly available historical stock data for NVIDIA (https://www.kaggle.com/datasets/avinashmynampati/nvidia-stock-volatility-20142024?resource=download). The data contains the following key columns:

Date: The date of the stock price entry.
Open: The opening stock price on the given date.
High: The highest stock price on the given date.
Low: The lowest stock price on the given date.
Close: The closing stock price on the given date.
Volume: The total trading volume for NVIDIA on the given date.
The dataset is stored in a CSV file named NVIDIA_Stock_Volatility_2014_2024.csv.

## What the App Does
This app analyzes and visualizes NVIDIA's stock data over time. Key features include:

A line chart showing the stock’s closing price (Close).
Additional lines representing the highest (High) and lowest (Low) stock prices for each day.
Provides insights into stock volatility over the years, helping users visualize fluctuations and trends in NVIDIA’s stock performance.

## How to Run and Deploy the App

1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run`

