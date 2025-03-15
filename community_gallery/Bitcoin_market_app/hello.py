from preswald import text, plotly, table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set up the dashboard title and description
text("# Bitcoin Market Analysis Dashboard")
text("### Historical Price and Volume Analysis")

# Load Bitcoin market data from a CSV file
df = pd.read_csv('data/Bitcoin.csv')

# Convert the 'Date' column from string format to a proper datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')

# Convert the 'Date' column back to a string format to avoid JSON serialization issues
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

# Create a candlestick chart to visualize Bitcoin's price movements over time
fig_candlestick = go.Figure(data=[
    go.Candlestick(
        x=df['Date'],  # Dates for the x-axis
        open=df['Open'],  # Opening prices
        high=df['High'],  # Highest prices
        low=df['Low'],  # Lowest prices
        close=df['Close'],  # Closing prices
        name='OHLC'  # Name of the candlestick chart
    )
])

# Customize the appearance of the candlestick chart
fig_candlestick.update_layout(
    title='Bitcoin Price History (OHLC)',  # Set chart title
    yaxis_title='Price (USD)',  # Label for the y-axis
    xaxis_title='Date',  # Label for the x-axis
    height=600,  # Set chart height
    template='plotly_white'  # Use a clean, white background theme
)

# Create a bar chart to show trading volume trends over time
fig_volume = px.bar(
    df,
    x='Date',  # Dates for the x-axis
    y='Volume',  # Trading volume for the y-axis
    title='Trading Volume Over Time',  # Set chart title
    height=400,  # Set chart height
    color_discrete_sequence=['rgba(0, 128, 255, 0.7)']  # Use a blue color for bars
)

# Customize the appearance of the volume chart
fig_volume.update_layout(
    yaxis_title='Volume (USD)',  # Label for the y-axis
    xaxis_title='Date',  # Label for the x-axis
    template='plotly_white'  # Use a clean, white background theme
)

# Extract key statistics from the dataset
latest_price = df['Close'].iloc[0]  # Most recent closing price
max_price = df['High'].max()  # Highest price ever recorded
min_price = df['Low'].min()  # Lowest price ever recorded
avg_volume = df['Volume'].mean() / 1e9  # Average daily trading volume in billions

# Display key statistics in the dashboard
text(f"### Key Statistics")
text(f"Latest Price: ${latest_price:,.2f}")  # Show latest Bitcoin price
text(f"All-Time High: ${max_price:,.2f}")  # Show highest price ever
text(f"All-Time Low: ${min_price:,.2f}")  # Show lowest price ever
text(f"Average Daily Volume: ${avg_volume:,.2f}B")  # Show average volume in billions

# Show the interactive candlestick chart
plotly(fig_candlestick)
text("")

# Show the interactive volume chart
plotly(fig_volume)
text("")

# Display a table with the first 10 rows of historical Bitcoin data
text("### Historical Data Table")
table(df.head(10))
