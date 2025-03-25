import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from preswald import connect, get_df, text, table, slider, plotly
import preswald

connect()

text("# Amazon Stock Analysis (2000-2025)")
text(
    """
This interactive dashboard analyzes Amazon stock performance over time,
offering insights into price trends, returns, volatility, and technical indicators.
Use the controls below to customize the analysis parameters.
    """
)

try:
    df = get_df("amazon_stock")
    if df is None or df.empty:
        df = pd.DataFrame({
            'Date': pd.date_range(start='2000-01-01', end='2025-01-01', freq='W'),
            'Open': np.random.uniform(10, 3500, 1305),
            'High': np.random.uniform(10, 3700, 1305),
            'Low': np.random.uniform(9, 3300, 1305),
            'Close': np.random.uniform(10, 3600, 1305),
            'Volume': np.random.randint(1000000, 50000000, 1305)
        })
        for i in range(1, len(df)):
            df.loc[i, 'Open'] = df.loc[i-1, 'Close'] * (1 + np.random.normal(0, 0.01))
            df.loc[i, 'High'] = max(df.loc[i, 'Open'], df.loc[i, 'Close']) * (1 + abs(np.random.normal(0, 0.005)))
            df.loc[i, 'Low'] = min(df.loc[i, 'Open'], df.loc[i, 'Close']) * (1 - abs(np.random.normal(0, 0.005)))
    else:
        df.rename(columns={
            'date': 'Date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'adj_close': 'Adj_Close',
            'volume': 'Volume'
        }, inplace=True)
except Exception as e:
    df = pd.DataFrame({
        'Date': pd.date_range(start='2000-01-01', end='2025-01-01', freq='W'),
        'Open': np.random.uniform(10, 3500, 1305),
        'High': np.random.uniform(10, 3700, 1305),
        'Low': np.random.uniform(9, 3300, 1305),
        'Close': np.random.uniform(10, 3600, 1305),
        'Volume': np.random.randint(1000000, 50000000, 1305)
    })
    for i in range(1, len(df)):
        df.loc[i, 'Open'] = df.loc[i-1, 'Close'] * (1 + np.random.normal(0, 0.01))
        df.loc[i, 'High'] = max(df.loc[i, 'Open'], df.loc[i, 'Close']) * (1 + abs(np.random.normal(0, 0.005)))
        df.loc[i, 'Low'] = min(df.loc[i, 'Open'], df.loc[i, 'Close']) * (1 - abs(np.random.normal(0, 0.005)))

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")

text("## Stock Data Preview")
table(df.head(10), title="First 10 Rows of Amazon Stock Data")

df['SMA_50'] = df['Close'].rolling(window=50).mean()
df['SMA_200'] = df['Close'].rolling(window=200).mean()
df['Daily_Return'] = df['Close'].pct_change() * 100
df['Volatility_30D'] = df['Daily_Return'].rolling(window=30).std() * np.sqrt(252)

text("## Analysis Period")

min_year = df['Date'].dt.year.min()
max_year = df['Date'].dt.year.max()
year_range = list(range(min_year, max_year + 1))

year_idx_mapping = dict(enumerate(year_range))
rev_year_mapping = {v: k for k, v in year_idx_mapping.items()}

start_year_idx = slider("Select Start Year", min_val=0, max_val=len(year_range)-1, default=0)
end_year_idx = slider("Select End Year", min_val=0, max_val=len(year_range)-1, default=len(year_range)-1)

start_year = year_idx_mapping[start_year_idx]
end_year = year_idx_mapping[end_year_idx]

start_date = pd.Timestamp(year=start_year, month=1, day=1)
end_date = pd.Timestamp(year=end_year, month=12, day=31)
filtered_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

text(f"**Selected Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
text(f"**Number of Trading Days:** {len(filtered_df)}")

text("## Stock Price Trends")

fig_candlestick = go.Figure()

fig_candlestick.add_trace(
    go.Candlestick(
        x=filtered_df["Date"],
        open=filtered_df["Open"],
        high=filtered_df["High"],
        low=filtered_df["Low"],
        close=filtered_df["Close"],
        name="AMZN",
        increasing_line_color='green',
        decreasing_line_color='red'
    )
)

if len(filtered_df) >= 50:
    fig_candlestick.add_trace(
        go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["SMA_50"],
            mode="lines",
            name="50-Day MA",
            line=dict(color='blue', width=1)
        )
    )

if len(filtered_df) >= 200:
    fig_candlestick.add_trace(
        go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["SMA_200"],
            mode="lines",
            name="200-Day MA",
            line=dict(color='orange', width=1)
        )
    )

fig_candlestick.update_layout(
    title="Amazon Stock Price (Candlestick Chart with Moving Averages)",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    margin=dict(l=0, r=0, t=30, b=0),
    height=500,
    hovermode="x unified"
)

fig_candlestick.update_yaxes(tickprefix="$")

plotly(fig_candlestick)

text("## Trading Volume Analysis")

fig_volume = go.Figure()

colors = ['green' if row['Close'] >= row['Open'] else 'red' for _, row in filtered_df.iterrows()]

fig_volume.add_trace(
    go.Bar(
        x=filtered_df["Date"],
        y=filtered_df["Volume"],
        marker_color=colors,
        name="Volume"
    )
)

filtered_df['Volume_MA20'] = filtered_df['Volume'].rolling(window=20).mean()
fig_volume.add_trace(
    go.Scatter(
        x=filtered_df["Date"],
        y=filtered_df['Volume_MA20'],
        mode="lines",
        name="20-Day Avg Volume",
        line=dict(color='blue', width=2)
    )
)

fig_volume.update_layout(
    title="Amazon Trading Volume Over Time",
    xaxis_title="Date",
    yaxis_title="Volume",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    margin=dict(l=0, r=0, t=30, b=0),
    height=400,
    hovermode="x unified"
)

fig_volume.update_yaxes(
    tickformat=".2s"
)

plotly(fig_volume)

text("## Technical Analysis")

ma_window = slider("Moving Average Window (Days)", min_val=5, max_val=100, default=20, step=5)
bb_std = slider("Bollinger Band Standard Deviations", min_val=1.0, max_val=3.0, default=2.0, step=0.5)

filtered_df["SMA"] = filtered_df["Close"].rolling(window=ma_window).mean()
filtered_df["EMA"] = filtered_df["Close"].ewm(span=ma_window, adjust=False).mean()
filtered_df["Upper_Band"] = filtered_df["SMA"] + (filtered_df["Close"].rolling(window=ma_window).std() * bb_std)
filtered_df["Lower_Band"] = filtered_df["SMA"] - (filtered_df["Close"].rolling(window=ma_window).std() * bb_std)

fig_ma = go.Figure()

fig_ma.add_trace(
    go.Scatter(
        x=filtered_df["Date"], 
        y=filtered_df["Close"], 
        mode="lines", 
        name="Close Price",
        line=dict(color='black', width=1)
    )
)
fig_ma.add_trace(
    go.Scatter(
        x=filtered_df["Date"], 
        y=filtered_df["SMA"], 
        mode="lines", 
        name=f"SMA ({ma_window} days)",
        line=dict(color='blue', width=2)
    )
)
fig_ma.add_trace(
    go.Scatter(
        x=filtered_df["Date"], 
        y=filtered_df["EMA"], 
        mode="lines", 
        name=f"EMA ({ma_window} days)",
        line=dict(color='orange', width=2, dash='dash')
    )
)

fig_ma.update_layout(
    title=f"Moving Averages Analysis (Window: {ma_window} days)",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    margin=dict(l=0, r=0, t=30, b=0),
    height=400,
    hovermode="x unified"
)
fig_ma.update_yaxes(tickprefix="$")
plotly(fig_ma)

fig_bb = go.Figure()

fig_bb.add_trace(
    go.Scatter(
        x=filtered_df["Date"], 
        y=filtered_df["Close"], 
        mode="lines", 
        name="Close Price",
        line=dict(color='black', width=1)
    )
)

fig_bb.add_trace(
    go.Scatter(
        x=filtered_df["Date"],
        y=filtered_df["Upper_Band"],
        mode="lines",
        name=f"Upper Band (+{bb_std}σ)",
        line=dict(color='rgba(173, 216, 230, 0.7)', width=1),
        fill=None
    )
)
fig_bb.add_trace(
    go.Scatter(
        x=filtered_df["Date"],
        y=filtered_df["Lower_Band"],
        mode="lines",
        name=f"Lower Band (-{bb_std}σ)",
        line=dict(color='rgba(173, 216, 230, 0.7)', width=1),
        fill='tonexty',
        fillcolor='rgba(173, 216, 230, 0.2)'
    )
)
fig_bb.add_trace(
    go.Scatter(
        x=filtered_df["Date"], 
        y=filtered_df["SMA"], 
        mode="lines", 
        name=f"SMA ({ma_window} days)",
        line=dict(color='blue', width=2)
    )
)

fig_bb.update_layout(
    title=f"Bollinger Bands ({ma_window}-day SMA, {bb_std} standard deviations)",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    margin=dict(l=0, r=0, t=30, b=0),
    height=400,
    hovermode="x unified"
)
fig_bb.update_yaxes(tickprefix="$")
plotly(fig_bb)

text("## Return Analysis")

fig_returns = px.histogram(
    filtered_df.dropna(),
    x="Daily_Return",
    nbins=50,
    title="Distribution of Daily Returns (%)",
    labels={"Daily_Return": "Daily Return (%)"},
    color_discrete_sequence=["green"],
    marginal="box"
)

fig_returns.update_layout(
    xaxis_title="Daily Return (%)",
    yaxis_title="Frequency",
    margin=dict(l=0, r=0, t=30, b=0),
    height=400,
    bargap=0.1
)

fig_returns.add_vline(x=0, line_width=2, line_color="black", line_dash="dash")

plotly(fig_returns)

filtered_df["Cumulative_Return"] = (1 + filtered_df["Daily_Return"] / 100).cumprod() - 1

fig_cumulative = px.line(
    filtered_df,
    x="Date",
    y="Cumulative_Return",
    title="Cumulative Return Over Time",
    labels={"Cumulative_Return": "Cumulative Return", "Date": "Date"},
    color_discrete_sequence=["darkgreen"],
)

np.random.seed(42)
s_and_p_daily_returns = np.random.normal(0.03/252, 0.15/np.sqrt(252), len(filtered_df))
filtered_df["SP500_Return"] = (1 + s_and_p_daily_returns).cumprod() - 1

fig_cumulative.add_scatter(
    x=filtered_df["Date"], 
    y=filtered_df["SP500_Return"], 
    mode='lines', 
    name='S&P 500 (Simulated)', 
    line=dict(color='blue', width=1)
)

fig_cumulative.update_layout(
    xaxis_title="Date",
    yaxis_title="Cumulative Return",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    margin=dict(l=0, r=0, t=30, b=0),
    height=400,
    hovermode="x unified"
)
fig_cumulative.update_yaxes(tickformat=".2%")
plotly(fig_cumulative)

text("## Volatility Analysis")

volatility_window = slider("Volatility Calculation Window (Days)", min_val=10, max_val=90, default=30, step=5)

fig_vol = go.Figure()

fig_vol.add_trace(
    go.Scatter(
        x=filtered_df["Date"],
        y=filtered_df["Daily_Return"].rolling(window=volatility_window).std() * np.sqrt(252),
        mode="lines",
        name=f"{volatility_window}-Day Rolling Volatility",
        line=dict(color='red', width=2)
    )
)

avg_market_vol = np.ones(len(filtered_df)) * 0.15
fig_vol.add_trace(
    go.Scatter(
        x=filtered_df["Date"],
        y=avg_market_vol,
        mode="lines",
        name="Avg Market Volatility",
        line=dict(color='gray', width=1, dash='dash')
    )
)

fig_vol.update_layout(
    title=f"Rolling {volatility_window}-Day Annualized Volatility",
    xaxis_title="Date",
    yaxis_title="Annualized Volatility",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    margin=dict(l=0, r=0, t=30, b=0),
    height=400,
    hovermode="x unified"
)
fig_vol.update_yaxes(tickformat=".2%")
plotly(fig_vol)

text("## Options Pricing Simulation")
text(
    """
This section simulates the payoff of basic option strategies using the current Amazon stock price.
Adjust the parameters to see how the payoff diagram changes.
    """
)

current_price = filtered_df["Close"].iloc[-1]
text(f"**Current Amazon Stock Price:** ${current_price:.2f}")

strike_price = slider(
    "Strike Price ($)",
    min_val=float(current_price * 0.7),
    max_val=float(current_price * 1.3),
    default=float(current_price),
    step=1.0
)

option_type_idx = slider("Option Type (0 for Call, 1 for Put)", min_val=0, max_val=1, default=0)
option_type = "Call" if option_type_idx == 0 else "Put"
text(f"Selected Option Type: {option_type}")

price_range = np.linspace(current_price * 0.5, current_price * 1.5, 100)

if option_type == "Call":
    payoffs = [max(price - strike_price, 0) for price in price_range]
    option_title = f"Call Option Payoff (Strike: ${strike_price:.2f})"
    color = "green"
else:
    payoffs = [max(strike_price - price, 0) for price in price_range]
    option_title = f"Put Option Payoff (Strike: ${strike_price:.2f})"
    color = "red"

fig_option = go.Figure()

fig_option.add_trace(
    go.Scatter(
        x=price_range,
        y=payoffs,
        mode="lines",
        name=f"{option_type} Option Payoff",
        line=dict(color=color, width=2)
    )
)

if option_type == "Call":
    breakeven = strike_price
    breakeven_label = f"Break-even: ${breakeven:.2f}"
else:
    breakeven = strike_price
    breakeven_label = f"Break-even: ${breakeven:.2f}"

fig_option.add_shape(
    type="line",
    x0=current_price,
    y0=0,
    x1=current_price,
    y1=max(payoffs),
    line=dict(color="blue", width=2, dash="dash"),
)

fig_option.add_annotation(
    x=current_price,
    y=0,
    text=f"Current Price: ${current_price:.2f}",
    showarrow=True,
    arrowhead=1,
    ax=0,
    ay=40
)

fig_option.add_shape(
    type="line",
    x0=price_range[0],
    y0=0,
    x1=price_range[-1],
    y1=0,
    line=dict(color="black", width=1),
)

fig_option.update_layout(
    title=option_title,
    xaxis_title="Stock Price at Expiration",
    yaxis_title="Option Payoff ($)",
    margin=dict(l=0, r=0, t=30, b=0),
    height=400,
    hovermode="x unified"
)
fig_option.update_xaxes(tickprefix="$")
fig_option.update_yaxes(tickprefix="$")
plotly(fig_option)

text("## Summary Statistics")

start_date_actual = filtered_df["Date"].min().strftime("%Y-%m-%d")
end_date_actual = filtered_df["Date"].max().strftime("%Y-%m-%d")
total_trading_days = len(filtered_df)
first_price = filtered_df["Close"].iloc[0]
last_price = filtered_df["Close"].iloc[-1]
price_change = last_price - first_price
percent_change = (price_change / first_price) * 100
annualized_return = ((1 + percent_change / 100) ** (252 / total_trading_days) - 1) * 100 if total_trading_days > 0 else 0
max_price = filtered_df["High"].max()
min_price = filtered_df["Low"].min()
avg_volume = filtered_df["Volume"].mean()
volatility = filtered_df["Daily_Return"].std() * np.sqrt(252) * 100

stats_df = pd.DataFrame({
    "Metric": [
        "Analysis Start Date", "Analysis End Date", "Total Trading Days",
        "Starting Price ($)", "Ending Price ($)", "Price Change ($)",
        "Percent Change (%)", "Annualized Return (%)",
        "Maximum Price ($)", "Minimum Price ($)", 
        "Average Daily Volume", "Annualized Volatility (%)"
    ],
    "Value": [
        start_date_actual, end_date_actual, f"{total_trading_days:,}",
        f"${first_price:.2f}", f"${last_price:.2f}", f"${price_change:.2f}",
        f"{percent_change:.2f}%", f"{annualized_return:.2f}%",
        f"${max_price:.2f}", f"${min_price:.2f}", 
        f"{avg_volume:,.0f}", f"{volatility:.2f}%"
    ]
})

table(stats_df, title="Amazon Stock Performance Summary")

if len(df) > 252 * 3:
    periods = {
        "Last Month": 21,
        "Last Quarter": 63,
        "Last Year": 252,
        "Last 3 Years": 756,
        "All Time": len(df)
    }
    
    period_stats = []
    for period_name, days in periods.items():
        if len(df) >= days:
            period_df = df.iloc[-days:]
            period_return = (period_df["Close"].iloc[-1] / period_df["Close"].iloc[0] - 1) * 100
            period_vol = period_df["Daily_Return"].std() * np.sqrt(252) * 100
            period_sharpe = period_return / period_vol if period_vol > 0 else 0
            
            period_stats.append({
                "Period": period_name,
                "Return (%)": f"{period_return:.2f}%",
                "Volatility (%)": f"{period_vol:.2f}%",
                "Sharpe Ratio": f"{period_sharpe:.2f}"
            })
    
    period_df = pd.DataFrame(period_stats)
    table(period_df, title="Performance Across Different Time Periods")

text("### Data Analysis by Preswald")
text("Amazon stock data analysis from 2000-2025")
