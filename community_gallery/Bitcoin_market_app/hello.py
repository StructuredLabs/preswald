from preswald import text, plotly, table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

text("# 📊 Bitcoin Market Analysis Dashboard")
text("## A Comprehensive Look at Bitcoin's Historical Trends")

df = pd.read_csv('data/Bitcoin.csv')

df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

df['MA_50'] = df['Close'].rolling(window=50).mean()
df['MA_200'] = df['Close'].rolling(window=200).mean()

text("### 📈 Bitcoin Price History (Candlestick Chart)")

fig_candlestick = go.Figure(data=[
    go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='OHLC'
    )
])

fig_candlestick.add_trace(go.Scatter(x=df['Date'], y=df['MA_50'], mode='lines', name='50-day MA', line=dict(color='blue', width=1.5)))
fig_candlestick.add_trace(go.Scatter(x=df['Date'], y=df['MA_200'], mode='lines', name='200-day MA', line=dict(color='red', width=1.5)))

fig_candlestick.update_layout(
    title='Bitcoin Price History (OHLC)',
    yaxis_title='Price (USD)',
    xaxis_title='Date',
    height=600,
    template='plotly_white'
)

plotly(fig_candlestick)

text("### 📊 Bitcoin Trading Volume Over Time")

fig_volume = px.bar(
    df,
    x='Date',
    y='Volume',
    title='Trading Volume Over Time',
    height=400,
    color_discrete_sequence=['rgba(0, 128, 255, 0.7)']
)

fig_volume.update_layout(
    yaxis_title='Volume (USD)',
    xaxis_title='Date',
    template='plotly_white'
)

plotly(fig_volume)

text("### 🔍 Bitcoin Price vs. Trading Volume")

df['Scaled_Volume'] = df['Volume'] / df['Volume'].max() * 100

fig_scatter = px.scatter(
    df, 
    x='Close', 
    y='Volume', 
    title='Bitcoin Price vs. Trading Volume', 
    labels={'Close': 'Bitcoin Price (USD)', 'Volume': 'Trading Volume (USD)'},
    color='Close', 
    size='Scaled_Volume',  
    height=500,
    color_continuous_scale='Viridis'
)

fig_scatter.update_layout(
    xaxis_title="Bitcoin Price (USD)",
    yaxis_title="Trading Volume (USD)",
    template="plotly_white"
)

plotly(fig_scatter)

text("### 🔥 Heatmap of Bitcoin Price Fluctuations")

df['Price Change'] = df['Close'] - df['Open']
fig_heatmap = px.density_heatmap(
    df,
    x='Date',
    y='Price Change',
    z='Volume',
    title='Heatmap of Bitcoin Price Changes',
    color_continuous_scale='Blues',
    height=500
)

plotly(fig_heatmap)

text("## 📌 Bitcoin Historical Insights & Key Events")

text("### 1️⃣ Bitcoin's Early Days (2009-2012)")
text("- Created by **Satoshi Nakamoto**, Bitcoin initially had little to no value.")
text("- In 2010, **Laszlo Hanyecz** made history by purchasing two pizzas for **10,000 BTC**.")
text("- The first major Bitcoin exchange, **Mt. Gox**, was established in 2010.")

text("### 2️⃣ First Bull Run & Volatility (2013-2017)")
text("- Bitcoin crossed **$1,000** for the first time in 2013 but crashed after China's regulations.")
text("- The **Mt. Gox hack** in 2014 led to a loss of **850,000 BTC**.")
text("- In **2017**, Bitcoin reached **$20,000** before a correction.")

text("### 3️⃣ Institutional Adoption (2018-2021)")
text("- Bitcoin dropped to **$3,000** in 2018 during a bear market.")
text("- The **COVID-19 pandemic** in 2020 increased institutional interest, with companies like **Tesla** and **MicroStrategy** investing in Bitcoin.")
text("- Bitcoin hit an **all-time high of $69,000 in November 2021**.")

text("### 4️⃣ Recent Trends (2022-Present)")
text("- In 2022, Bitcoin crashed due to rising interest rates, the **collapse of Terra Luna**, and the **FTX bankruptcy**.")
text("- Bitcoin started recovering in **2023-2024**, with growing institutional adoption.")

text("### 📊 Key Market Statistics")

latest_price = df['Close'].iloc[-1]
max_price = df['High'].max()
min_price = df['Low'].min()
avg_volume = df['Volume'].mean() / 1e9  

text(f"📌 **Latest Bitcoin Price**: **${latest_price:,.2f}**")
text(f"📌 **All-Time High**: **${max_price:,.2f}**")
text(f"📌 **All-Time Low**: **${min_price:,.2f}**")
text(f"📌 **Average Daily Trading Volume**: **${avg_volume:,.2f}B**")

text("### 📜 Historical Data Table")
table(df.head(10))
