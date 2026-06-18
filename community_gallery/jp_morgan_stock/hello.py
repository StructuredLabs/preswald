import preswald as pw
import pandas as pd
import plotly.express as px

pw.text(
    "# JPMorgan Chase Stock Data Visualization (1980 - 2025)\n"
    "## Context\n"
    "JPMorgan Chase & Co. is an American multinational financial services firm headquartered in New York City and incorporated in Delaware. It is the largest bank in the United States and the world's largest bank by market capitalization as of 2023.\n"
    "### End of Day Market Cap According to Different Sources\n"
    "On Mar 3rd, 2025, the market cap of JPMorgan Chase was reported to be:\n"
    "- **$728.72 Billion USD** by Yahoo Finance\n"
    "- **$728.72 Billion USD** by CompaniesMarketCap\n"
    "- **$728.74 Billion USD** by Nasdaq\n"
    "### Content\n"
    "**Geography:** USA  \n"
    "**Time period:** March 1980 - March 2025  \n"
    "**Unit of analysis:** Amazon Stock Data 2025"
)

data_fields = {
    "Variable": ["date", "open", "high", "low", "close", "adj_close", "volume"],
    "Description": [
        "date",
        "The price at market open.",
        "The highest price for that day.",
        "The lowest price for that day.",
        "The price at market close, adjusted for splits.",
        "The closing price after adjustments for all applicable splits and dividend distributions. "
        "Data is adjusted using appropriate split and dividend multipliers, adhering to "
        "Center for Research in Security Prices (CRSP) standards.",
        "The number of shares traded on that day."
    ]
}
data_fields_df = pd.DataFrame(data_fields)
pw.table(data_fields_df, title="JPMorgan Chase Stock Data Fields")

# Initialize connection to preswald.toml data sources
pw.connect()  

# Load the dataset
df = pd.read_csv("data/JPM_1940-01-01_2025-03-04.csv") 
pw.table(df.tail(10), "JPMorgan Chase Stock Data (Latest 10 rows)")

# Convert date to datetime and string for JSON serialization
df["date"] = pd.to_datetime(df["date"], utc=True).astype(str)

# Define Outstanding Shares
outstanding_shares = 2.8e9  

# Helper Function for Annotation Formatting
def add_annotation(fig, df, column, label, format_type="billions"):
    latest = df.iloc[-1]
    value = latest[column]

    # Format billions with commas or EPS with 2 decimals
    if format_type == "billions":
        formatted_value = f"${value / 1e9:,.2f}B"
    else:
        formatted_value = f"${value:.2f} EPS"

    fig.add_annotation(
        x=latest["date"],
        y=value,
        text=f"{formatted_value}\n{latest['date']}",
        showarrow=True,
        arrowhead=2,
        font=dict(size=12, color="black"),
    )

# SECTION 1: Market Cap
pw.text("## Market Cap \nAs of March 2025 JPMorgan Chase has a market cap of $728.72 Billion USD. This makes JPMorgan Chase the world's 14th most valuable company by market cap according to our data. The market capitalization, commonly called market cap, is the total market value of a publicly traded company's outstanding shares and is commonly used to measure how much a company is worth.")

df["market_cap"] = df["close"] * outstanding_shares  

market_cap_fig = px.area(
    df, x="date", y="market_cap",
    title="Market Cap History of JPMorgan Chase",
    labels={"date": "Year", "market_cap": "Market Cap (in billions)"},
    template="plotly_white"
)

market_cap_fig.update_layout(
    yaxis=dict(tickprefix="$", tickformat=".2s"),
    xaxis_title="Year",
    yaxis_title="Market Cap (in billions)",
    hovermode="x unified",
)

add_annotation(market_cap_fig, df, "market_cap", "Market Cap")
pw.plotly(market_cap_fig)


# SECTION 2: Revenue
pw.text("## Revenue \nAccording to JPMorgan Chase's latest financial reports the company's current revenue (TTM ) is $177.41 Billion USD. an increase over the revenue in the year 2023 that were of $155.29 Billion USD. The revenue is the total amount of income that a company generates by the sale of goods or services. Unlike with the earnings no expenses are subtracted.")

df["revenue"] = df["volume"] * df["close"]

revenue_fig = px.area(
    df, x="date", y="revenue",
    title="Revenue History of JPMorgan Chase",
    labels={"date": "Year", "revenue": "Revenue (in billions)"},
    template="plotly_white"
)

revenue_fig.update_layout(
    yaxis=dict(tickprefix="$", tickformat=".2s"),
    xaxis_title="Year",
    yaxis_title="Revenue (in billions)",
    hovermode="x unified",
)

add_annotation(revenue_fig, df, "revenue", "Revenue")
pw.plotly(revenue_fig)


# SECTION 3: Earnings
pw.text("## Earnings \nAccording to JPMorgan Chase's latest financial reports the company's current earnings are $177.41 Billion USD. , an increase over its 2023 earnings that were of $61.61 Billion USD. The earnings displayed on this page is the company's Pretax Income.")

df["earnings"] = df["revenue"] / outstanding_shares

earnings_fig = px.area(
    df, x="date", y="earnings",
    title="Earnings History of JPMorgan Chase",
    labels={"date": "Year", "earnings": "Earnings per Share (EPS)"},
    template="plotly_white"
)

earnings_fig.update_layout(
    yaxis_title="Earnings per Share (EPS in USD)",
    xaxis_title="Year",
    hovermode="x unified",
)

add_annotation(earnings_fig, df, "earnings", "Earnings", format_type="eps")
pw.plotly(earnings_fig)
