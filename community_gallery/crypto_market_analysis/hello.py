from preswald import text, plotly, connect, get_df, table, query, slider, selectbox, Workflow
import pandas as pd
import plotly.express as px


text("# Cryptocurrency Market Analysis 📈")


workflow = Workflow()

@workflow.atom()
def load_data():
    connect()
    df = get_df("coins_csv")
    return df

@workflow.atom(dependencies=["load_data"])
def preprocess_data(load_data):
    df = load_data.copy()
    
    # Convert timestamp
    df["last_updated"] = pd.to_datetime(df["last_updated"], unit="s", errors="coerce")
    df["last_updated"] = df["last_updated"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Convert numeric columns
    numeric_cols = ["market_cap_usd", "price_usd", "percent_change_24h", "percent_change_1h", "available_supply"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    # Drop missing values in necessary columns
    df = df.dropna(subset=["percent_change_24h", "market_cap_usd", "price_usd"])

    df["coingecko_url"] = df["id"].apply(lambda coin_id: f"https://www.coingecko.com/en/coins/{coin_id}")

    return df

@workflow.atom(dependencies=["preprocess_data"])
def format_currency(preprocess_data):
    df = preprocess_data.copy()
    
    # Format USD values
    df["market_cap_display"] = df["market_cap_usd"].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    df["price_display"] = df["price_usd"].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")

    return df

@workflow.atom(dependencies=["format_currency"])
def filter_data(format_currency):
    df = format_currency.copy()
    threshold = slider("Market Cap Threshold (USD)", min_val=1_000_000, max_val=50_000_000_000, default=1_000_000_000)
    return df[df["market_cap_usd"] > threshold]

@workflow.atom(dependencies=["filter_data"])  # Now sorting happens AFTER filtering
def sort_data(filter_data):
    df = filter_data.copy()
    sort_column = selectbox("Sort by", ["price_usd", "market_cap_usd", "percent_change_24h", "percent_change_1h"])
    sort_order = selectbox("Sort order", ["Ascending", "Descending"])
    ascending = True if sort_order == "Ascending" else False
    return df.sort_values(by=sort_column, ascending=ascending)

@workflow.atom(dependencies=["filter_data"])
def scatter_plot(filter_data):
    df = filter_data.copy()
    fig = px.scatter(
        df,
        x="market_cap_usd",
        y="price_usd",
        color="percent_change_24h",
        hover_name="name",
        size=df["available_supply"].pow(0.3),
        title="Market Cap vs. Price of Cryptocurrencies (24h Change)",
        log_x=True,
        log_y=True,
        color_continuous_scale="RdYlGn",
    )

    fig.update_traces(marker=dict(sizemode='area', sizemin=5))
    fig.update_coloraxes(showscale=False)
    fig.update_layout(template="plotly_white", xaxis_title="Market Cap (Log Scale)", yaxis_title="Price (Log Scale)")

    return fig

@workflow.atom(dependencies=["filter_data"])
def bar_chart(filter_data):
    df = filter_data.copy()
    df_top = df.sort_values(by="market_cap_usd", ascending=False).head(10)

    fig = px.bar(
        df_top,
        x="name",
        y="market_cap_usd",
        title="Top Cryptocurrencies by Market Cap",
        labels={"market_cap_usd": "Market Cap (USD)", "name": "Cryptocurrency"},
        hover_data=["market_cap_display"],
        color_discrete_sequence=["#1f77b4"],
    )

    fig.update_layout(xaxis_tickangle=45, height=500, title_x=0.5)

    return fig

@workflow.atom(dependencies=["filter_data"])
def line_chart(filter_data):
    df = filter_data.copy()
    df_top = df.sort_values(by="market_cap_usd", ascending=False).head(15)

    fig = px.line(
        df_top,
        x="name",
        y="percent_change_24h",
        title="24h Price Change of Top Cryptocurrencies",
        markers=True,
        labels={"name": "Cryptocurrency", "percent_change_24h": "24h % Change"},
        line_shape="spline",
    )

    fig.update_traces(marker=dict(sizemode='area', sizemin=10, opacity=0.7))
    fig.update_layout(margin=dict(l=40, r=40, t=40, b=40), height=600)


    return fig

# Execute workflow
results = workflow.execute()



# Display filtered data first
table(results["filter_data"].value[["name", "symbol", "market_cap_display", "price_display", "percent_change_24h"]], 
      title="Cryptos with Market Cap Above Selected Threshold")

# Updated display for clickable crypto names in hello.py
sorted_df = results["sort_data"].value.copy()

sorted_df["name"] = sorted_df.apply(
    lambda row: f"[{row['name']}]({row['coingecko_url']})", axis=1
)

# Create markdown table
md_table = """
| Name | Symbol | Market Cap | Price | 24h % Change |
|------|--------|------------|-------|--------------|
"""

for _, row in sorted_df.iterrows():
    md_table += f"| {row['name']} | {row['symbol']} | {row['market_cap_display']} | {row['price_display']} | {row['percent_change_24h']}% |\n"

# Display clickable markdown table
text("# Sorted Cryptocurrency Data (Click for Details)")
text(md_table)

# Display visualizations
plotly(results["scatter_plot"].value)
plotly(results["bar_chart"].value)
plotly(results["line_chart"].value)
