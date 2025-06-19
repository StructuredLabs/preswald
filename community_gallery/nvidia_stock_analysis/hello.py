import plotly.express as px
from preswald import connect, get_df, plotly, slider, table, text
import pandas as pd

# Initialize Preswald connection
connect()
df = get_df("NVIDIA")

# Ensure 'Date' column exists before processing
if 'Date' not in df.columns:
    text("⚠️ Error: 'Date' column not found in dataset. Please check your data format.")
else:
    # Convert 'Date' to datetime format for filtering
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Handle invalid dates
    df['Year'] = df['Date'].dt.year.astype(int)  # Extract year
    df['Date'] = df['Date'].astype(str)  # Convert Date to string

    # Section 1: Title and Summary Statistics
    text("# NVIDIA Stock Volatility Analysis (2014-2024)")
    text("Explore historical stock trends, returns, and volatility.")

    # Show summary stats
    table(df.describe(), title="📊 Summary Statistics")

    # Section 2: Interactive Filters
    text("## 2. 🔍 Select Analysis Year")
    selected_year = slider("Choose Year", min_val=int(df['Year'].min()), max_val=int(df['Year'].max()), default=int(df['Year'].max()))
    filtered_df = df[df['Year'] == selected_year]

    # Select metric for analysis
    text("## 2(a). 📈 Select a Stock Metric")
    metric_options = ["Close", "High", "Low", "Open", "Volume", "Daily_Return", "Rolling_Volatility", "ATR"]
    metric = metric_options[0]  # Default metric is 'Close'

    # Section 3: Dynamic Stock Trend Visualization
    text("## 3. 📊 Stock Trends Over Time")
    fig_trend = px.line(filtered_df, x='Date', y=metric, title=f'{metric} Over Time', template='plotly_dark')
    plotly(fig_trend)

    # Section 4: Bollinger Bands Visualization
    text("## 4. 📉 Bollinger Bands Analysis")
    fig_bollinger = px.line(filtered_df, x='Date', y=['Rolling_Mean', 'Upper_Band', 'Lower_Band'], title="Bollinger Bands Over Time")
    plotly(fig_bollinger)

    # Section 5: Distribution Analysis
    text("## 5. 📊 Distribution of Returns")
    fig_dist = px.histogram(filtered_df, x='Daily_Return', nbins=50, title="Distribution of Daily Returns", template='plotly_dark')
    plotly(fig_dist)

    # Section 6: Volume Analysis
    text("## 6. 📊 Trading Volume Over Time")
    fig_volume = px.bar(filtered_df, x='Date', y='Volume', title="Trading Volume Per Day", template='plotly_dark')
    plotly(fig_volume)

    # Section 7: Data Table for Exploration
    table(filtered_df, title="📜 Filtered Stock Data")
