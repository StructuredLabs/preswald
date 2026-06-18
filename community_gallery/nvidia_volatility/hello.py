"""
NVIDIA Stock Volatility Dashboard

This is the main entry point for the Preswald dashboard.
It uses Preswald's built-in components for data visualization.
"""

# Import required modules
import pandas as pd
import numpy as np
from preswald import text, table, plotly, slider, connect, get_df
import plotly.express as px
import plotly.graph_objects as go

# Dashboard title
text("# NVIDIA Stock Volatility Dashboard 📈")
text("### Interactive analysis of NVIDIA stock price volatility")

# Connect to data source
connect()

# Load NVIDIA stock data
nvidia_data = get_df('nvidia_stock')

# Convert Date column to string to avoid JSON serialization issues
nvidia_data['Date'] = nvidia_data['Date'].astype(str)

# Display basic information
text("## Stock Overview")
table(nvidia_data.head(10))

# Add date range slider for filtering
text("## Select Date Range")

# Get unique dates as strings for the sliders
date_values = sorted(nvidia_data['Date'].unique())

# Create sliders using indices instead of actual dates
start_date_idx = slider("Start Date Index", 
                       min_val=0,
                       max_val=len(date_values)-1,
                       default=0)

end_date_idx = slider("End Date Index", 
                     min_val=0,
                     max_val=len(date_values)-1,
                     default=len(date_values)-1)

# Get the actual date strings from the indices
start_date = date_values[start_date_idx]
end_date = date_values[end_date_idx]

# Display selected date range
text(f"### Selected Date Range: {start_date} to {end_date}")

# Filter data based on selected date range
filtered_data = nvidia_data[(nvidia_data['Date'] >= start_date) & 
                           (nvidia_data['Date'] <= end_date)]

# Calculate volatility (using rolling standard deviation of returns)
text("## Volatility Analysis")

# Calculate daily returns
filtered_data['Daily_Return'] = filtered_data['Close'].pct_change() * 100

# Calculate 20-day rolling volatility
filtered_data['Volatility_20d'] = filtered_data['Daily_Return'].rolling(window=20).std()

# Create stock price chart
price_fig = px.line(filtered_data, x='Date', y='Close', 
                   title='NVIDIA Stock Price',
                   labels={'Close': 'Price ($)', 'Date': 'Date'})
price_fig.update_layout(template='plotly_white')
plotly(price_fig)

# Create volatility chart
vol_fig = px.line(filtered_data, x='Date', y='Volatility_20d',
                 title='NVIDIA 20-Day Rolling Volatility',
                 labels={'Volatility_20d': 'Volatility (%)', 'Date': 'Date'})
vol_fig.update_layout(template='plotly_white')
plotly(vol_fig)

# Volume analysis
text("## Trading Volume Analysis")
volume_fig = px.bar(filtered_data, x='Date', y='Volume',
                   title='NVIDIA Trading Volume',
                   labels={'Volume': 'Volume', 'Date': 'Date'})
volume_fig.update_layout(template='plotly_white')
plotly(volume_fig)

# Summary statistics
text("## Summary Statistics")
summary_stats = pd.DataFrame({
    'Metric': ['Mean Price', 'Max Price', 'Min Price', 'Mean Daily Return (%)', 'Mean Volatility (%)'],
    'Value': [
        filtered_data['Close'].mean(),
        filtered_data['Close'].max(),
        filtered_data['Close'].min(),
        filtered_data['Daily_Return'].mean(),
        filtered_data['Volatility_20d'].mean()
    ]
})
table(summary_stats)

text("### Dashboard created with Preswald") 