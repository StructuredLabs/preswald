from preswald import text, plotly, connect, get_df, table, query, slider
import plotly.express as px
import pandas as pd

connect()

stock_df = get_df('sample_csv')

sql = "SELECT * FROM sample_csv WHERE volume > 10000 LIMIT 10;"
filtered_df = query(sql, "sample_csv")

text("# Stock Market Data Viewer")

table(filtered_df, title="Top Stocks with High Volume")

# Custom Visualization: High vs. Closing Prices
table(filtered_df)

# Ensure numeric columns
filtered_df["high"] = pd.to_numeric(filtered_df["high"], errors="coerce")
filtered_df["close"] = pd.to_numeric(filtered_df["close"], errors="coerce")
filtered_df["date"] = filtered_df["date"].astype(str)  # Ensure date is string

# Drop missing values
filtered_df = filtered_df.dropna(subset=["high", "close"])

if not filtered_df.empty:
    text("# Opening vs. Closing Prices")
    fig = px.scatter(filtered_df, x='high', y='close', text='date',
                     title='High vs. Closing Prices',
                     labels={'high': 'Highest Price', 'close': 'Closing Price'})
    fig.update_traces(textposition='top center', marker=dict(size=12, color='blue'))
    fig.update_layout(template='plotly_white')
    plotly(fig)
else:
    text("No data available for plotting. Adjust your filters.")

text("# Volume-Based Stock Filtering")
text("### Please select a minimum volume threshold to filter stocks.")
thresh = slider("volume", min_val=5000, max_val=100000, default=20000)
dynamic_df = filtered_df[filtered_df["volume"] > thresh]
table(dynamic_df, title="Filtered Stocks by Volume")

text("# Stock Price Trends Over Time")

stock_df["date"] = pd.to_datetime(stock_df["date"]).dt.strftime("%Y-%m-%d")
fig = px.line(stock_df, x="date", y="close", title="Stock Closing Prices Over Time")
plotly(fig)