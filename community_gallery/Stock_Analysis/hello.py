from preswald import text, plotly, connect, get_df, table, selectbox, text_input, button
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Title and Description
text("# Stock Analysis")
text("This is an example of a stock analysis dashboard using Preswald. You can select the chart type, timeframe, and indicator to analyze the stock price data.")

# Load the CSV
connect() 
df_google = get_df('google_csv')

# User selections for charting options
chart_type = selectbox("Select Chart Type", options=["Line Chart", "Candlestick Chart"], default="Candlestick Chart")
timeframe = selectbox("Select Timeframe", options=["1W", "1M", "1Y", "5Y"], default="1Y")
indicator = selectbox("Select Indicator", options=["SMA", "EMA", "RSI", "Bollinger Bands", "None"], default="SMA")

# Optional user input for indicator period
indicator_period_input = text_input("Indicator Period", placeholder="Enter the period for the indicator")
if indicator_period_input and not indicator_period_input.isdigit():
    text("Please enter a valid number for the indicator period.")
    indicator_period = 20  # Default value if input is invalid
elif indicator_period_input:
    indicator_period = int(indicator_period_input)
else:
    indicator_period = 20  # Default period if no input

############################################################################################################
# Filter data based on the selected timeframe
############################################################################################################

# Ensure proper datetime conversion for filtering
df_google["DateTime"] = pd.to_datetime(df_google["Date"])  
latest_date = df_google["DateTime"].max()

# Determine start date based on selected timeframe
if timeframe == "1W":
    start_date = latest_date - pd.DateOffset(weeks=1)
elif timeframe == "1M":
    start_date = latest_date - pd.DateOffset(months=1)
elif timeframe == "1Y":
    start_date = latest_date - pd.DateOffset(years=1)
else:  # "5Y"
    start_date = latest_date - pd.DateOffset(years=5)

# Filter and sort the data for plotting
filtered_df_google = df_google[df_google["DateTime"] >= start_date]
sorted_df_google = filtered_df_google.sort_values("DateTime")

############################################################################################################
# Plotting utility functions for different indicators and price traces
############################################################################################################

def plot_price(df, color='blue', width=3):
    # Plot basic price line
    return go.Scatter(
        x=df['Date'],
        y=df['Close'],
        mode='lines',
        name='Price',
        line=dict(color=color, width=width)
    )

def plot_MA(df_internal, color='black', width=1, window=20):
    # Calculate Simple Moving Average (SMA)
    df = df_internal.copy()
    df['MA'] = df['Close'].rolling(window=window).mean()

    trace = go.Scatter(
        x=df['Date'],
        y=df['MA'],
        mode='lines',
        name=f"SMA ({indicator_period})",
        line=dict(color=color, width=width)
    )

    # Determine bullish or bearish signal
    stock_direction = "Bullish" if df['Close'].iloc[-1] > df['MA'].iloc[-1] else "Bearish"
    return trace, stock_direction

def plot_EMA(df_internal, color='green', width=1, window=20):
    # Calculate Exponential Moving Average (EMA)
    df = df_internal.copy()
    df['EMA'] = df['Close'].ewm(span=window, adjust=False).mean()

    trace = go.Scatter(
        x=df['Date'],
        y=df['EMA'],
        mode='lines',
        name=f"EMA ({window})",
        line=dict(color=color, width=width)
    )

    stock_direction = "Bullish" if df['Close'].iloc[-1] > df['EMA'].iloc[-1] else "Bearish"
    return trace, stock_direction    

def plot_candlestick(df):
    # Create candlestick trace
    return go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    )

def plot_volume(df):
    # Volume plot (currently not used for 1Y as per final decision)
    return go.Bar(
        x=df['Date'],
        y=df['Volume'],
        name='Vol'
    )

def plot_rsi(df_internal: pd.DataFrame, period: int = 14, price_column: str = 'close') -> go.Figure:
    df = df_internal.copy()
    delta = df[price_column].diff()

    # Calculate gains and losses
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    # Compute exponential moving averages of gains and losses
    roll_up = pd.Series(gain).ewm(span=period, adjust=False).mean()
    roll_down = pd.Series(loss).ewm(span=period, adjust=False).mean()

    # Compute RSI
    RS = roll_up / roll_down
    RSI = 100 - (100 / (1 + RS))
    df['RSI'] = RSI

    # Plot RSI
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['RSI'],
        mode='lines',
        name=f'RSI ({period})',
        line=dict(color='blue', width=2)
    ))

    # Add standard RSI bands
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")

    fig.update_layout(
        title=f"RSI ({period}-period)",
        yaxis_title='RSI Value',
        xaxis_title='Date',
        template='plotly_white',
        height=400
    )

    # Determine market condition based on RSI value
    if df['RSI'].iloc[-1] > 70:
        stock_direction = "Bearish"
    elif df['RSI'].iloc[-1] < 30:
        stock_direction = "Bullish"
    else:
        stock_direction = "Neutral"
    
    return fig, stock_direction

def plot_bollinger_bands(df_internal, window=20, num_std=2):
    # Calculate Bollinger Bands
    df = df_internal.copy()
    df['MA'] = df['Close'].rolling(window=window).mean()
    df['STD'] = df['Close'].rolling(window=window).std()

    df['Upper'] = df['MA'] + (df['STD'] * num_std)
    df['Lower'] = df['MA'] - (df['STD'] * num_std)

    # Create band traces
    ma_trace = go.Scatter(
        x=df['Date'],
        y=df['MA'],
        mode='lines',
        name=f"Bollinger MA ({window})",
        line=dict(color='orange')
    )
    upper_trace = go.Scatter(
        x=df['Date'],
        y=df['Upper'],
        mode='lines',
        name='Upper Band',
        line=dict(color='green', dash='dash')
    )
    lower_trace = go.Scatter(
        x=df['Date'],
        y=df['Lower'],
        mode='lines',
        name='Lower Band',
        line=dict(color='red', dash='dash')
    )

    # Check for overbought/oversold condition
    if df['Close'].iloc[-1] > df['Upper'].iloc[-1]:
        stock_direction = "Overbought"
    elif df['Close'].iloc[-1] < df['Lower'].iloc[-1]:
        stock_direction = "Oversold"
    else:
        stock_direction = "Neutral"

    return [ma_trace, upper_trace, lower_trace], stock_direction

############################################################################################################
# Plot the chart based on user selection and indicator
############################################################################################################

price_trace = plot_price(sorted_df_google, color='blue', width=3)
candlestick_trace = plot_candlestick(sorted_df_google)

# Select the main chart type
chart_trace = candlestick_trace if chart_type == "Candlestick Chart" else price_trace
stock_direction = None

# Conditional plotting based on the selected indicator
if indicator == "SMA":
    MA_trace, stock_direction  = plot_MA(sorted_df_google, color='black', width=1, window=indicator_period)
    fig = go.Figure([MA_trace, chart_trace])
    fig.update_layout(
        title='Stock Price Analysis',
        xaxis_title='Date',
        yaxis_title='Close',
        template='plotly_white'
    )
    plotly(fig)

elif indicator == "EMA":
    EMA_trace, stock_direction = plot_EMA(sorted_df_google, color='green', width=1, window=indicator_period)
    fig = go.Figure([EMA_trace, chart_trace])
    fig.update_layout(
        title='Stock Price Analysis',
        xaxis_title='Date',
        yaxis_title='Close',
        template='plotly_white'
    )
    plotly(fig)

elif indicator == "RSI":
    rsi_trace, stock_direction = plot_rsi(sorted_df_google, period=indicator_period, price_column='Close')
    fig = go.Figure([chart_trace])
    fig.update_layout(
        title='Stock Price Analysis',
        xaxis_title='Date',
        yaxis_title='Close',
        template='plotly_white'
    )
    plotly(fig)
    plotly(rsi_trace)  # RSI is plotted separately

elif indicator == "Bollinger Bands":
    bb_traces, stock_direction = plot_bollinger_bands(sorted_df_google, window=indicator_period, num_std=2)
    fig = go.Figure([chart_trace] + bb_traces)
    fig.update_layout(
        title='Stock Price Analysis with Bollinger Bands',
        xaxis_title='Date',
        yaxis_title='Close',
        template='plotly_white'
    )
    plotly(fig)

else:
    # No indicator selected, plot only the price
    fig = go.Figure([chart_trace])
    fig.update_layout(
        title='Stock Price Analysis',
        xaxis_title='Date',
        yaxis_title='Close',
        template='plotly_white'
    )
    plotly(fig)

############################################################################################################
# Analysis, Description and Table
############################################################################################################
text(f"Stock Direction: {stock_direction}")

# Compute key price statistics over the selected timeframe
low_price = filtered_df_google["Low"].min()
high_price = filtered_df_google["High"].max()
average_price = filtered_df_google["Close"].mean()

# Display statistics
text(f"Lowest Price : ${low_price:.2f}\n\nHighest Price: ${high_price:.2f}\n\nAverage Price: ${average_price:.2f}")

# Render data table for reference
table(filtered_df_google, title=f"Stock Price Data of Google Over {timeframe}")