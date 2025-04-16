from preswald import text, plotly, connect, get_df, table, selectbox, button
import pandas as pd
import plotly.express as px
import numpy as np

text("# Welcome to US Stock Market Analysis (2020-2024) 📈")
text("Interactive analysis of stock, commodities, and crypto data.")

connect()
df = get_df("us_stock_market")

market_sectors = {
    "Cryptocurrency": [
        "Bitcoin",
        "Ethereum"
    ],
    "Tech Stocks": [
        "Apple",
        "Microsoft",
        "Amazon",
        "Tesla",
        "Google",
        "Meta",
        "Nvidia",
        "Netflix"
    ],
    "Financial": [
        "Berkshire"
    ],
    "Indices": [
        "S&P_500",
        "Nasdaq_100"
    ],
    "Commodities": [
        "Gold",
        "Silver",
        "Crude_oil",
        "Natural_Gas",
        "Copper",
        "Platinum"
    ]
}

# Create formatted options with disabled sector headers
formatted_options = []
for sector, stocks in market_sectors.items():
    formatted_options.append(f"[DISABLED] {sector}")  # Add disabled prefix to make it non-selectable
    formatted_options.extend(stocks)

selected_name = selectbox(
    "Select First Stock",
    options=formatted_options,
    default="Nasdaq_100",
)

selected_name2 = selectbox(
    "Select Second Stock",
    options=formatted_options,
    default="Nasdaq_100"
)

text("Tip: You can select multiple stocks to compare their prices. 📊")

# Update the validation to check for disabled items
if "[DISABLED]" in selected_name:
    selected_name = "Nasdaq_100"
if "[DISABLED]" in selected_name2:
    selected_name2 = "Nasdaq_100"

selected_stock = f"{selected_name}_Price"
selected_stock2 = f"{selected_name2}_Price"

df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

df = df.sort_values('Date')


fig = px.line(
    df,
    x="Date",
    y=[selected_stock, selected_stock2],  
    title=f"Price Trends Comparison: {selected_name} vs {selected_name2}",
    labels={"Date": "Date", "value": "Price (USD)", "variable": "Stock"},
    markers=False
)

fig.update_traces(
    line={"width": 3},
    marker={"size": 8}
)

fig.for_each_trace(lambda t: t.update(name=t.name.replace("_Price", "")))

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    xaxis_tickangle=45,
    height=500,
    legend_title="Stocks"
)

plotly(fig)

text("**Quick Fact ⚡**: Apple became the first $3 trillion company in 2022. 🍏 With iPhone revenue crossing $200 billion annually, Apple isn't selling phones—it's selling an ecosystem. 🔗💰")

text("## Stock Analysis Heatmap")

volume_cols = []
price_cols = []

for sector, stocks in market_sectors.items():
    for stock in stocks:
        if stock == "S&P_500":
            volume_cols.append("S&P_500_Vol.")
            price_cols.append("S&P_500")
        elif stock == "Nasdaq_100":
            volume_cols.append("Nasdaq_100_Vol.")  
            price_cols.append("Nasdaq_100_Price")  
        else:
            volume_cols.append(f"{stock}_Vol.")
            price_cols.append(f"{stock}_Price")

for vol_col in volume_cols:
    if vol_col in df.columns:
        volume_data = pd.to_numeric(df[vol_col], errors='coerce')
        total_volume = volume_data.fillna(0).sum()

analysis_data = []
for vol_col, price_col in zip(volume_cols, price_cols):
    stock_name = vol_col.replace('_Vol.', '')
    stock_name = stock_name.replace('Vol.', '')
    
    if vol_col in df.columns and price_col in df.columns:
        volume_data = pd.to_numeric(df[vol_col], errors='coerce')
        price_data = pd.to_numeric(df[price_col], errors='coerce')
        
        total_volume = volume_data.fillna(0).sum()
        avg_price = price_data.fillna(0).mean()
        
        if total_volume > 0 and avg_price > 0:
            analysis_data.append({
                'stock': stock_name.strip('_'),  
                'total_volume': float(total_volume),
                'avg_price': float(avg_price)
            })

analysis_df = pd.DataFrame(analysis_data)

if not analysis_df.empty:
    analysis_df = analysis_df.sort_values('total_volume', ascending=False)
    top_16 = analysis_df.head(16)

    avg_volume = top_16['total_volume'].mean()
    max_volume = top_16['total_volume'].max()
    min_volume = top_16['total_volume'].min()

    max_deviation = max(max_volume - avg_volume, avg_volume - min_volume)
    
    heatmap_data = top_16['total_volume'].values.reshape(4, 4)
    stock_names = top_16['stock'].values.reshape(4, 4)  
    heatmap_data = np.flipud(heatmap_data)
    stock_names = np.flipud(stock_names)  
    
    def format_volume(val):
        if val >= 1e9:  
            return f"{val/1e9:.1f}B"
        else:  
            return f"{val/1e6:.1f}M"
    
    text_data = [[f"{stock.replace('_', ' ')}<br>{format_volume(val)}" for stock, val in zip(row_names, row_vals)] 
                 for row_names, row_vals in zip(stock_names, heatmap_data)]
    
    fig_heatmap = px.imshow(
        heatmap_data,
        aspect='auto',
        title="Top 16 Stocks by Overall Trading Volume",
        color_continuous_scale=[
            (0, 'rgb(200,255,200)'),      # Very Light Green (for lower values)
            (0.0005, 'rgb(144,238,144)'),    # Light Green
            (0.0025, 'rgb(255,255,255)'),    # White (will be at average)
            (0.005, 'rgb(102,204,102)'),    # Medium Dark Green
            (1, 'rgb(0,102,0)')           # Dark Green (for higher values)
        ],
        zmin=max(0, avg_volume - max_deviation),
        zmax=avg_volume + max_deviation
    )

    fig_heatmap.update_traces(
        text=text_data,
        texttemplate="%{text}",
        textfont={"size": 12},
        showscale=True
    )

    fig_heatmap.update_layout(
        height=600,
        width=1000,
    )

    plotly(fig_heatmap)
else:
    text("No valid data found for creating the heatmap.")

text("**Quick Fact ⚡**: Nasdaq 100 soared +54% in 2023, led by AI stocks. 🤖📈 It's not just an index—it's a bet on the future of technology.")

sector_growth = {}

for sector, stocks in market_sectors.items():
    total_sector_growth = 0
    valid_stocks = 0
    
    for stock in stocks:
        if stock in ["SP_500", "Nasdaq_100"]:
            possible_cols = [stock, f"{stock}_Price"]
            price_col = next((col for col in possible_cols if col in df.columns), None)
        else:
            price_col = f"{stock}_Price"
        
        if price_col and price_col in df.columns:
            price_data = pd.to_numeric(df[price_col], errors='coerce').dropna()
            
            if not price_data.empty:
                first_price = price_data.iloc[0]  
                last_price = price_data.iloc[-1]  
                
                if first_price > 0:  
                    stock_growth = ((last_price - first_price) / first_price) * 100
                    total_sector_growth += stock_growth
                    valid_stocks += 1
    
    if valid_stocks > 0:
        avg_sector_growth = total_sector_growth / valid_stocks
        sector_growth[sector] = round(avg_sector_growth, 2)

growth_df = pd.DataFrame(list(sector_growth.items()), columns=['Sector', 'Growth'])

text("## Sector-wise Growth Bar Chart")
fig_growth = px.bar(
    growth_df.sort_values(by="Growth", ascending=True),
    x="Growth",
    y="Sector",
    text="Growth",
    title="Sector-wise Growth (2020-2024)",
    labels={
        "Growth": "Growth (%)",
        "Sector": "Market Sector"
    },
    orientation='h',
    color="Growth",
    color_continuous_scale=[
        (0, 'rgb(144,238,144)'),   # Light green
        (0.25, 'rgb(34,139,34)'),  # Forest green
        (0.75, 'rgb(0,128,0)'),    # Medium dark green
        (1, 'rgb(0,100,0)'),       # Dark green
    ]
)

fig_growth.update_traces(
    texttemplate='%{text:.1f}%',
    textposition='outside'
)

fig_growth.update_layout(
    height=400,
    xaxis_title="Growth (%)",
    yaxis_title="Market Sector",
    yaxis_tickangle=0,  
    showlegend=False
)

plotly(fig_growth)

text("**Quick Fact ⚡**: Ethereum's transition to Proof-of-Stake in 2022 reduced energy consumption by 99.95% ⚡🌱, while its market cap stayed above $400 billion in 2024, proving sustainability and scalability can coexist. 💰")

text("## Market Sentiment")

year_ranges = ["Overall", "2020-21", "2021-22", "2022-23", "2023-24"]
selected_year_range = selectbox("Select Time Period", options=year_ranges, default="Overall")

time_period = "Overall" if selected_year_range == "Overall" else selected_year_range

sentiment_data = []
for sector, stocks in market_sectors.items():
    for stock in stocks:
        if stock in ["SP_500", "Nasdaq_100"]:
            price_col = stock
        else:
            price_col = f"{stock}_Price"
        
        if price_col in df.columns:
            df[f'{stock}_return'] = pd.to_numeric(df[price_col], errors='coerce').pct_change()
            sentiment_data.append(df[f'{stock}_return'])

all_returns = pd.concat(sentiment_data, axis=1)

df['avg_daily_return'] = all_returns.mean(axis=1)

if selected_year_range != "Overall":
    start_year = int(selected_year_range.split("-")[0])
    end_year = int("20" + selected_year_range.split("-")[1])
    
    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'])
    
    filtered_df = df[
        (df['Date'].dt.year >= start_year) & 
        (df['Date'].dt.year <= end_year)
    ]
else:
    filtered_df = df

def classify_sentiment(return_val):
    if pd.isna(return_val):
        return 'Neutral'
    elif return_val > 0.02:
        return 'Strong Positive'
    elif return_val > 0:
        return 'Weak Positive'
    elif return_val < -0.02:
        return 'Strong Negative'
    elif return_val < 0:
        return 'Weak Negative'
    else:
        return 'Neutral'

filtered_df['daily_sentiment'] = filtered_df['avg_daily_return'].apply(classify_sentiment)

sentiment_counts = filtered_df['daily_sentiment'].value_counts()

positive_days = sentiment_counts.get('Strong Positive', 0) + sentiment_counts.get('Weak Positive', 0)
negative_days = sentiment_counts.get('Strong Negative', 0) + sentiment_counts.get('Weak Negative', 0)
total_days = positive_days + negative_days

if total_days > 0:  
    positive_percent = (positive_days / total_days) * 100
    negative_percent = (negative_days / total_days) * 100
else:
    positive_percent = 0
    negative_percent = 0

time_period = "Overall" if selected_year_range == "Overall" else selected_year_range

sentiment_df = pd.DataFrame({
    'Sentiment': ['Positive', 'Negative'],
    'Percentage': [positive_percent, negative_percent]
})

fig_sentiment = px.pie(
    sentiment_df,
    values='Percentage',
    names='Sentiment',
    title=f'Market Sentiment Distribution ({time_period})',
    color='Sentiment',
    color_discrete_map={
        'Positive': 'rgb(0,204,0)',
        'Negative': 'rgb(213,0,0)'
    }
)

fig_sentiment.update_traces(textinfo='percent+label')
plotly(fig_sentiment)

text("**Quick Fact ⚡**: When Satya Nadella said, 'AI is the defining technology of our time,' Wall Street laughed. 🤖😂 Then Microsoft's AI-powered Azure skyrocketed to $100B+ in revenue. 🚀💰")

text("## Leaderboard: Top 5 stocks in terms of profit")

sector_options = list(market_sectors.keys()) + ["Overall"]
selected_sector = selectbox("Select Market Sector", options=sector_options, default="Tech Stocks")

profit_data = []

if selected_sector == "Overall":
    sectors_to_process = market_sectors.items()
else:
    sectors_to_process = [(selected_sector, market_sectors[selected_sector])]

for sector, stocks in sectors_to_process:
    for stock in stocks:
        if stock in ["S&P_500", "Nasdaq_100"]:
            possible_cols = [stock, f"{stock}_Price"]
            col = next((col for col in possible_cols if col in df.columns), None)
        else:
            col = f"{stock}_Price"
            
        try:
            if col and col in df.columns:  
                price_data = pd.to_numeric(df[col], errors='coerce').dropna()
                
                if len(price_data) >= 2:  
                    final_price = price_data.iloc[-1]  
                    initial_price = price_data.iloc[0]  
                    
                    if initial_price > 0:
                        profit_percentage = ((final_price - initial_price) / initial_price) * 100
                        
                        profit_data.append({
                            'Stock': stock,
                            'Sector': sector,
                            'Profit (%)': round(profit_percentage, 2),
                            'Initial Price': round(initial_price, 2),
                            'Final Price': round(final_price, 2)
                        })
        except Exception as e:
            continue

if profit_data:  
    profit_df = pd.DataFrame(profit_data)
    profit_df = profit_df.sort_values('Profit (%)', ascending=False)
else:
    profit_df = pd.DataFrame(columns=['Stock', 'Sector', 'Profit (%)', 'Initial Price', 'Final Price'])

if selected_sector != "Overall" and len(profit_df) < 5:
    num_padding = 5 - len(profit_df)
    padding_data = []
    for i in range(num_padding):
        padding_data.append({
            'Stock': f'No Stock {i+1}',
            'Sector': selected_sector,
            'Profit (%)': 0.0,
            'Initial Price': 0.0,
            'Final Price': 0.0
        })
    padding_df = pd.DataFrame(padding_data)
    profit_df = pd.concat([profit_df, padding_df])

top_5_stocks = profit_df.head(5)

fig_top_stocks = px.bar(
    top_5_stocks,
    x='Stock',
    y='Profit (%)',
    title=f'Top 5 Most Profitable Stocks ({selected_sector} Sector)' if selected_sector != "Overall" else 'Top 5 Most Profitable Stocks (Overall)',
    text='Profit (%)',
    color='Profit (%)',
    color_continuous_scale=[
        (0, 'rgb(144,238,144)'),   # Light green
        (0.25, 'rgb(0,204,0)'),   # Bright green
        (0.75, 'rgb(0,153,0)'),   # Medium dark green
        (1, 'rgb(0,102,0)')      # Dark green
    ],
    hover_data=['Initial Price', 'Final Price']  
)

fig_top_stocks.update_traces(
    hovertemplate="<b>%{x}</b><br>" +
                  "Profit: %{y:.2f}%<br>" +
                  "First Price (2020): $%{customdata[0]:.2f}<br>" +
                  "Last Price (2024): $%{customdata[1]:.2f}<br>" +
                  "<extra></extra>"
)

fig_top_stocks.update_traces(
    texttemplate='%{text:.1f}%',
    textposition='outside'
)
fig_top_stocks.update_layout(
    xaxis_title="Stock",
    yaxis_title="Profit (%)",
    xaxis_tickangle=45,
    height=500,
    showlegend=False
)

plotly(fig_top_stocks)

if selected_sector != "Overall":
    sector_facts = {
        "Cryptocurrency": "**Quick Fact ⚡**: Bitcoin surged from $6,900 in March 2020 to an all-time high of $69,000 in 2021, before dipping to $16,000 in 2022 and rebounding past $100,000 in 2024. 🚀 Volatile? Yes. Profitable? Also yes. 💰",
        "Tech Stocks": "**Quick Fact ⚡**: Nvidia is just a GPU company'—that's what people said before its AI chips became a $60B business. 🎮➡️🤖 Now it's the most critical company in AI. 🚀💰",
        "Financial": "**Quick Fact ⚡**: Warren Buffett's Berkshire Hathaway has delivered a +3,787,464% return since 1965. 🏆 Investing in quality is still undefeated. 💵",
        "Indices": "**Quick Fact ⚡**: Nasdaq 100 soared +54% in 2023, led by AI stocks. 📊 It's not just an index—it's a bet on the future of technology. 🤖",
        "Commodities": "**Quick Fact ⚡**: Gold hit an all-time high of $2,450 per ounce in 2024, proving once again that when uncertainty rises, 🌟 gold shines. 🏆"
    }
    
    text(sector_facts[selected_sector])

text("#### **Developed by**: Nayan Katiyara, nayankatiyara03@gmail.com")
