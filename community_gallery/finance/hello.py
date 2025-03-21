import numpy as np
import pandas as pd
import plotly.express as px

from preswald import plotly, text


# 1. Dashboard Title and description
text("# Analyzing Stock Data Cleaning and Volatility")
text(
    "Here we will explore how standardization can effect the analysis of financial data."
)

# 2. Stock Price Comparison Plot
# load data
df = pd.read_csv("data/stock_data.csv")
df = df.reset_index()


df_melted = df.melt(
    id_vars=["index"],
    value_vars=[col for col in df.columns if col != "index"],
    var_name="Stock",
    value_name="Price",
)

# Create the figure
fig1 = px.line(
    df_melted,
    x="index",
    y="Price",
    color="Stock",
    title="Stock Price Comparison<br> <sup>Top 10 Stocks By Market Cap Over The Past Year</sup>",
    template="plotly_white",
    labels={"index": "Time Period", "Price": "Stock Price", "Stock": "Company"},
)

# Update the layout
fig1.update_layout(
    hovermode="x unified",
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    legend={"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 1},
    title={
        "y": 0.95,
        "x": 0.5,
    },
)

text("## Raw Data")
plotly(fig1)

# 3. Create Volatility heatmap to show difference in volatilites between pairs of stocks

# Compute returns
returns = df.pct_change().dropna()

# Compute volatility (standard deviation of returns)
volatilities = returns.std()

# Create heatmap matrix
tickers = df.columns
volatility_diff = np.zeros((len(tickers), len(tickers)))
for i, ticker1 in enumerate(tickers):
    for j, ticker2 in enumerate(tickers):
        vol_diff = abs(volatilities[ticker1] - volatilities[ticker2])
        volatility_diff[i, j] = vol_diff

df_volatility = pd.DataFrame(volatility_diff, index=tickers, columns=tickers)

fig2 = px.imshow(
    df_volatility,
    labels={"x": "Stock", "y": "Stock", "color": "Volatility Difference (stdev)"},
    title="Stock Volatility Comparison Heatmap",
    color_continuous_scale="Viridis",
)

fig2.update_layout(
    width=800,
    height=800,
    xaxis_title="Stock",
    yaxis_title="Stock",
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    title={
        "y": 0.95,
        "x": 0.5,
    },
)

fig2.update_xaxes(tickangle=45)
plotly(fig2)

text(
    "As can be seen in the plot, even among the top 10 stocks ranked by market cap, there exist significant discrepancies in the absolute value of shares. We are interested in the differences in volatility between securities, and want to preserve them while reducing the large discrepancies in absolute value, as these differences cause unwanted biases in any predictions made by models which use this data. To conduct any sort of meaningful analysis, we will need to somehow normalize the data."
)

# 4. Plot logarithmic returns and volatility of log returns
# We want to show that the price data can be normalized to a much closer range while preserving the volatility dynamics of the priced data.

text("## Logarithmic Returns")

# compute log returns
stock_cols = [col for col in df.columns if col != "index"]
tickers = stock_cols
df_clean = df.replace(0, np.nan).dropna()
log_returns = np.log(df_clean[stock_cols] / df_clean[stock_cols].shift(1)).dropna()

# Line plot of log returns
log_returns_melted = log_returns.reset_index().melt(
    id_vars=["index"], value_vars=stock_cols, var_name="Stock", value_name="Return"
)

fig3 = px.line(
    log_returns_melted,
    x="index",
    y="Return",
    color="Stock",
    title="Logarithmic Returns Over Time",
    template="plotly_white",
    labels={"index": "Trading Days", "Return": "Log Return", "Stock": "Company"},
)

fig3.update_layout(
    hovermode="x unified",
    legend={"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 1},
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    title={
        "text": "Logarithmic Returns<br><sup>Natural log of price ratios between consecutive days</sup>",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    },
)

plotly(fig3)

# 5. Show that log returns preserve the volatility relationship between securities while normalizing the price difference

# Compute volatility (standard deviation of log returns)
log_volatility = log_returns.std()

# Create heatmap matrix for log return volatility differences
log_volatility_diff = np.zeros((len(tickers), len(tickers)))
for i, ticker1 in enumerate(tickers):
    for j, ticker2 in enumerate(tickers):
        vol_diff = abs(log_volatility[ticker1] - log_volatility[ticker2])
        log_volatility_diff[i, j] = vol_diff

df_log_volatility = pd.DataFrame(log_volatility_diff, index=tickers, columns=tickers)

fig4 = px.imshow(
    df_log_volatility,
    labels={"x": "Stock", "y": "Stock", "color": "Log Volatility Difference (stdev)"},
    title="Log Returns Volatility Comparison Heatmap",
    color_continuous_scale="Viridis",
)

fig4.update_layout(
    width=800,
    height=800,
    xaxis_title="Stock",
    yaxis_title="Stock",
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    title={
        "y": 0.95,
        "x": 0.5,
    },
)

fig4.update_xaxes(tickangle=45)

# Display the heatmap
plotly(fig4)

text(
    "As you can see, the volatility relationships are more or less preserved, but the log returns are in a much closer range of one another in comparison to the raw price data."
)

text("# Extra Graphs:")

# 6. Show how volatility evolves over time in different stocks
text("## Rolling Window Volatility Analysis")

stock_cols = [col for col in df.columns if col != "index"]

# Compute percentage returns
returns = df[stock_cols].pct_change().dropna()

# Compute rolling volatility (e.g., 30-day rolling standard deviation)
rolling_window = 30

# Check if rolling window size is valid
if rolling_window > len(returns):
    raise ValueError(
        f"Rolling window size ({rolling_window}) cannot be larger than the number of rows in the returns DataFrame ({len(returns)})."
    )

rolling_volatility = returns.rolling(window=rolling_window).std()
rolling_volatility = rolling_volatility.dropna()

# Reset index
rolling_volatility_melted = rolling_volatility.reset_index()
rolling_volatility_melted["index"] = rolling_volatility_melted["index"].astype(int)

# Melt DataFrame for plotting
rolling_volatility_melted = rolling_volatility_melted.melt(
    id_vars=["index"], value_vars=stock_cols, var_name="Stock", value_name="Volatility"
)

# Plot rolling volatility
fig5 = px.line(
    rolling_volatility_melted,
    x="index",
    y="Volatility",
    color="Stock",
    title=f"{rolling_window}-Day Rolling Volatility",
    template="plotly_white",
    labels={
        "index": "Trading Days",
        "Volatility": "Volatility (stdev)",
        "Stock": "Company",
    },
)

fig5.update_layout(
    hovermode="x unified",
    legend={"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 1},
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    title={
        "text": f"{rolling_window}-Day Rolling Volatility<br><sup>Standard deviation of returns over a rolling window</sup>",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    },
)

plotly(fig5)

# 7. Plot the distribution of the returns
text("## Distribution of Returns")

# Melt the data for plotting
returns_melted = returns.reset_index().melt(
    id_vars=["index"], value_vars=stock_cols, var_name="Stock", value_name="Return"
)

# Box plot for returns
fig6 = px.box(
    returns_melted,
    x="Return",
    color="Stock",
    title="Box Plot of Daily Returns",
    template="plotly_white",
    labels={"Return": "Daily Return", "Stock": "Company"},
)

# Combine the contour plot and box plot (if desired)
fig6.update_layout(
    hovermode="x unified",
    legend={"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 1},
    xaxis={
        "range": [-0.2, 0.2]  # Set the range of x-axis from -2 to 2
    },
    xaxis_fixedrange=True,  # Lock x-axis zoom
    yaxis_fixedrange=True,  # Lock y-axis zoom
    title={
        "text": "Box Plot of Daily Returns<br><sup>Box plot for daily returns distribution</sup>",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    },
    title_x=0.5,
    title_y=0.95,
)

plotly(fig6)

# 8. Show the total drawdown (how much you are down on an investment from the previous high at a given time)
text("## Drawdown in Returns")

# Compute drawdowns
cumulative_returns = (1 + returns).cumprod()
peak = cumulative_returns.cummax()
drawdown = (cumulative_returns - peak) / peak

# Melt the data for plotting
drawdown_melted = drawdown.reset_index().melt(
    id_vars=["index"], value_vars=stock_cols, var_name="Stock", value_name="Drawdown"
)

# Plot drawdowns
fig7 = px.line(
    drawdown_melted,
    x="index",
    y="Drawdown",
    color="Stock",
    title="Drawdown Analysis",
    template="plotly_white",
    labels={"index": "Trading Days", "Drawdown": "Drawdown", "Stock": "Company"},
)

fig7.update_layout(
    hovermode="x unified",
    legend={"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 1},
    xaxis_fixedrange=True,
    yaxis_fixedrange=True,
    title={
        "text": "Drawdown Analysis<br><sup>Peak-to-trough decline in cumulative returns</sup>",
        "y": 0.95,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "top",
    },
)

plotly(fig7)
