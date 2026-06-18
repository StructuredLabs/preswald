from preswald import text, plotly, connect, get_df, table, text_input, slider
import pandas as pd
import os
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA

# Paths Definition
STOCKS_FOLDER = "data/stocks"
META_FILE = "data/symbols_valid_meta.csv"

# Display app heading and intro
text("# 📈 Welcome to StockFlow")
text("## Explore and analyze stock market data, visualize trends, and make informed decisions.")

# Load the stock metadata (list of valid symbols)
meta_df = pd.read_csv(META_FILE)
all_symbols = meta_df['Symbol'].tolist()

# Filter symbols that have CSV files available
valid_symbols = [symbol for symbol in all_symbols if os.path.exists(os.path.join(STOCKS_FOLDER, f"{symbol}.csv"))]

# Create dictionaries for metadata
symbol_to_company = pd.Series(meta_df['Security Name'].values, index=meta_df['Symbol']).to_dict()

# Connect to Preswald's data system
connect()

# Caching mechanism to avoid reloading stock data repeatedly
stock_data_cache = {}

# Function to load and preprocess stock data with caching
def load_stock_data(symbol):
    if symbol in stock_data_cache:
        return stock_data_cache[symbol]
    
    stock_file = os.path.join(STOCKS_FOLDER, f"{symbol}.csv")
    if os.path.exists(stock_file):
        stock_df = pd.read_csv(stock_file)
        stock_df.dropna(subset=['Date', 'Close'], inplace=True)
        stock_df['Date'] = pd.to_datetime(stock_df['Date'], errors='coerce')
        stock_df.set_index('Date', inplace=True)
        stock_df.index = stock_df.index.strftime('%Y-%m-%d')

        # Compute Bollinger Bands
        stock_df['SMA_20'] = stock_df['Close'].rolling(window=20).mean()
        stock_df['EMA_20'] = stock_df['Close'].ewm(span=20, adjust=False).mean()
        stock_df['STD_20'] = stock_df['Close'].rolling(window=20).std()
        stock_df['Upper_BB'] = stock_df['SMA_20'] + (stock_df['STD_20'] * 2)
        stock_df['Lower_BB'] = stock_df['SMA_20'] - (stock_df['STD_20'] * 2)

        stock_data_cache[symbol] = stock_df
        return stock_df
    return None

# Function to find top gainers and losers
def get_top_gainers_losers(period=30):
    stock_changes = []
    
    for symbol in valid_symbols:
        stock_data = load_stock_data(symbol)
        if stock_data is not None and len(stock_data) > period:
            recent_close = stock_data['Close'].iloc[-1]
            past_close = stock_data['Close'].iloc[-period]
            change_pct = ((recent_close - past_close) / past_close) * 100
            stock_changes.append((symbol, symbol_to_company.get(symbol, "Unknown"), change_pct))

    # Convert to DataFrame and sort
    stock_changes_df = pd.DataFrame(stock_changes, columns=["Stock Symbol", "Company Name", "Change (%)"])
    stock_changes_df.sort_values(by="Change (%)", ascending=False, inplace=True)

    # Top 5 gainers and losers
    top_gainers = stock_changes_df.head(5)
    top_losers = stock_changes_df.tail(5)

    return top_gainers, top_losers

# Display top gainers and losers
text("### 📈 Top Gainers & 📉 Top Losers in the Market")
time_period = slider("Select Time Period (Days)", min_val=7, max_val=90, default=30)

top_gainers, top_losers = get_top_gainers_losers(time_period)

text("#### 🚀 Top 5 Gainers")
table(top_gainers)

text("#### 📉 Top 5 Losers")
table(top_losers)

# Function to plot Time Series + Volume Bars + Bollinger Bands
def plot_stock_trends():
    fig = go.Figure()
    
    selected_symbols = ["AAPL", "TSLA"]
    available_symbols = [symbol for symbol in selected_symbols if symbol in valid_symbols]

    for symbol in available_symbols:
        stock_data = load_stock_data(symbol)
        if stock_data is not None:
            # Line chart for stock price
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['Close'],
                mode='lines',
                name=f"{symbol} Stock Price",
                line=dict(width=2)
            ))

            # Bollinger Bands
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['Upper_BB'],
                mode='lines',
                name=f"{symbol} Upper Limit (Price Threshold)",
                line=dict(dash='dot')
            ))

            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['Lower_BB'],
                mode='lines',
                name=f"{symbol} Lower Limit (Price Threshold)",
                line=dict(dash='dot')
            ))

    # Layout adjustments
    fig.update_layout(
        title="Stock Trends with Upper and Lower Price Thresholds (AAPL & TSLA)",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        legend=dict(x=0, y=1),
        showlegend=True
    )

    return fig

# Display the updated visualization
plotly(plot_stock_trends())

# Create a dataframe for available stocks
symbol_df = pd.DataFrame({
    "Stock Symbol": valid_symbols,
    "Company Name": [symbol_to_company.get(symbol, "Unknown") for symbol in valid_symbols],
    "Exchange": [meta_df.loc[meta_df['Symbol'] == symbol, 'Listing Exchange'].values[0] if symbol in meta_df['Symbol'].values else "Unknown" for symbol in valid_symbols]
})

# Display available stocks table
text("### 🏢 List of Available Stocks for Analysis")
table(symbol_df)

# Function to plot candlestick chart
def plot_candlestick_chart(symbol, stock_df):
    fig = go.Figure(data=[go.Candlestick(
        x=stock_df.index,
        open=stock_df['Open'],
        high=stock_df['High'],
        low=stock_df['Low'],
        close=stock_df['Close'],
        name=f"{symbol} Price Movement"
    )])

    fig.update_layout(
        title=f"{symbol} - Price Movement (Candlestick)",
        xaxis_title="Date",
        yaxis_title="Price ($)"
    )
    return fig

# Function to plot volume vs. price scatter plot
def plot_volume_vs_price(symbol, stock_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stock_df['Volume'],
        y=stock_df['Close'],
        mode='markers',
        marker=dict(color='blue', opacity=0.6),
        name="Volume vs. Price"
    ))

    fig.update_layout(
        title=f"{symbol} - Volume vs. Stock Price",
        xaxis_title="Volume",
        yaxis_title="Price ($)"
    )
    return fig

# Function to plot stock moving averages
def plot_moving_averages(symbol, stock_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['Close'], mode='lines', name="Closing Price"))
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['SMA_20'], mode='lines', name="20-Day Average Price (SMA)", line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['EMA_20'], mode='lines', name="Exponential Average (EMA)", line=dict(color='purple')))

    fig.update_layout(
        title=f"{symbol} - Moving Averages",
        xaxis_title="Date",
        yaxis_title="Price ($)"
    )
    return fig

# Function to generate time series forecast
def forecast_stock(symbol, stock_df, periods=30):
    model = ARIMA(stock_df['Close'], order=(5,1,0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=periods)

    future_dates = pd.date_range(stock_df.index[-1], periods=periods+1, freq='D')[1:]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=stock_df.index,
        y=stock_df['Close'],
        mode='lines',
        name="Historical Data",
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=future_dates.strftime('%Y-%m-%d'),
        y=forecast,
        mode='lines',
        name="Forecast (Next 30 Days)",
        line=dict(dash='dash', color='red')
    ))

    fig.update_layout(
        title=f"{symbol} - 30-Day Stock Price Forecast",
        xaxis_title="Date",
        yaxis_title="Price ($)"
    )
    return fig

# User input for stock analysis
text("### 📊 Enter a Stock Symbol to Start Your Analysis!")
user_input = text_input("Type the stock symbol here", "")
time_range = slider("Select Time Range (Days)", min_val=7, max_val=90, default=30)

if user_input and user_input in valid_symbols:
    user_stock_data = load_stock_data(user_input)
    if user_stock_data is not None:
        text(f"## {user_input} - Stock Performance Overview")

        # Display performance table
        stock_overview_df = pd.DataFrame({
            "Metric": ["Latest Close Price", "Highest Price", "Lowest Price", "Total Volume Traded"],
            "Value": [
                f"${user_stock_data['Close'].iloc[-1]:.2f}",
                f"${user_stock_data['High'].max():.2f}",
                f"${user_stock_data['Low'].min():.2f}",
                f"{user_stock_data['Volume'].sum():,.0f}"
            ]
        })
        table(stock_overview_df)

        # Display charts
        plotly(plot_candlestick_chart(user_input, user_stock_data))
        plotly(plot_volume_vs_price(user_input, user_stock_data))
        plotly(plot_moving_averages(user_input, user_stock_data))
        plotly(forecast_stock(user_input, user_stock_data))

        # Display recent stock data table
        table(user_stock_data.tail(10))
    else:
        text(f"Sorry, we couldn't retrieve data for {user_input}.")
