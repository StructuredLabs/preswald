from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff  # for the correlation heatmap

# Dashboard Title
text("# Amazon Stock Data Dashboard")
text("Explore Amazon stock data (2000-2025).")

# Load Data
connect()
df = get_df('amazon')

df = get_df('amazon')
df['date'] = pd.to_datetime(df['date'])  # Convert to datetime
df['date'] = df['date'].dt.strftime('%Y-%m-%d')  # Convert to string for JSON serialization


#  Scatter Plot: Volume vs. Close
text("## Volume vs. Close Price")
text("This scatter plot visualizes the relationship between trading volume and the closing price of Amazon stock. It helps identify whether higher trading volumes are associated with higher or lower closing prices.")

fig_scatter = px.scatter(
    df,
    x='volume',
    y='close',
    title='Volume vs. Closing Price',
    labels={'volume': 'Volume', 'close': 'Close Price (USD)'},
    template='plotly_white'
)
plotly(fig_scatter)

text("## Daily Returns Distribution")
text("This histogram shows the distribution of daily returns for Amazon stock. It helps identify the volatility and risk associated with the stock.")
# Distribution of Daily Returns
df['daily_return'] = df['close'].pct_change()
fig_returns = px.histogram(
    df.dropna(subset=['daily_return']),  # remove rows with NaN in daily_return
    x='daily_return',
    nbins=50,
    title='Distribution of Daily Returns',
    labels={'daily_return': 'Daily Return'},
    template='plotly_white'
)
plotly(fig_returns)

text("## Correlation Matrix")
text("This heatmap displays the correlation matrix for the numeric columns in the dataset. It helps identify the relationships between different variables in the dataset.")
#  Correlation Heatmap
numeric_cols = ['open', 'high', 'low', 'close', 'adj_close', 'volume']
corr_matrix = df[numeric_cols].corr()

fig_corr = ff.create_annotated_heatmap(
    z=corr_matrix.values,
    x=corr_matrix.columns.tolist(),
    y=corr_matrix.columns.tolist(),
    colorscale='Viridis',
    showscale=True
)
fig_corr.update_layout(title='Correlation Matrix', template='plotly_white')
plotly(fig_corr)


text("## Time Series Plots")
text("This line chart shows the closing price of Amazon stock over time. It helps identify trends, patterns, and significant changes in the stock's performance over the years.")
# Time Series Plot: Closing Price Over Time
fig_time_series = px.line(
    df,
    x='date',
    y='close',
    title='Closing Price Over Time',
    labels={'date': 'Date', 'close': 'Close Price (USD)'},
    template='plotly_white'
)
plotly(fig_time_series)


text("## Moving Averages")
text("This chart overlays the closing price with 50-day and 200-day moving averages. Moving averages smooth out price data to help identify trends and potential support or resistance levels.")

# Calculate Moving Averages
df['ma_50'] = df['close'].rolling(window=50).mean()
df['ma_200'] = df['close'].rolling(window=200).mean()

# Plot Moving Averages
fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(x=df['date'], y=df['close'], mode='lines', name='Close Price'))
fig_ma.add_trace(go.Scatter(x=df['date'], y=df['ma_50'], mode='lines', name='50-Day MA'))
fig_ma.add_trace(go.Scatter(x=df['date'], y=df['ma_200'], mode='lines', name='200-Day MA'))
fig_ma.update_layout(
    title='Closing Price with Moving Averages',
    xaxis_title='Date',
    yaxis_title='Price (USD)',
    template='plotly_white'
)
plotly(fig_ma)

text("## Candlestick Chart")
text("This candlestick chart provides a detailed view of the stock's price movements for each day, including the opening, high, low, and closing prices. It is commonly used in technical analysis to identify patterns and trends")
# Candlestick Chart
fig_candlestick = go.Figure(data=[go.Candlestick(
    x=df['date'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close'],
    name='Candlestick'
)])
fig_candlestick.update_layout(
    title='Candlestick Chart',
    xaxis_title='Date',
    yaxis_title='Price (USD)',
    template='plotly_white'
)
plotly(fig_candlestick)


text("## Volume Bar Chart")
text("This bar chart shows the trading volume of Amazon stock over time. It helps identify periods of high or low trading activity, which may indicate investor interest or significant events.")

# Volume Bar Chart
fig_volume = px.bar(
    df,
    x='date',
    y='volume',
    title='Trading Volume Over Time',
    labels={'date': 'Date', 'volume': 'Volume'},
    template='plotly_white'
)
plotly(fig_volume)

# Table Preview
text("## Data Preview")
table(df.head(10))
