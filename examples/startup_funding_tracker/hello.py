import pandas as pd
import plotly.express as px

from preswald import get_df, plotly, table, text


# Title & Intro
text("# 🚀 Startup Funding Tracker")
text("Visualize startup funding trends across industries and years.")

# Load data
df = get_df("startup_data")

# Show sample data
table(df)

# 📊 Summary statistics
df["amount_million"] = pd.to_numeric(df["amount_million"], errors="coerce")
total_funding = df["amount_million"].sum()
unique_startups = df["startup"].nunique()
years = f"{df['year'].min()} - {df['year'].max()}"

text(f"**Total Funding:** ${total_funding:,.2f}M")
text(f"**Unique Startups:** {unique_startups}")
text(f"**Years Covered:** {years}")

# 💼 Funding Amount by Industry
text("## 💼 Funding Amount by Industry")
df_industry = df.groupby("industry", as_index=False)["amount_million"].sum()
fig1 = px.bar(
    df_industry,
    x="industry",
    y="amount_million",
    color="industry",
    title="Total Funding by Industry",
    labels={"amount_million": "Funding (in $M)"},
    color_discrete_sequence=px.colors.qualitative.Safe,
)
fig1.update_layout(template="plotly_white", title_x=0.5)
fig1.update_yaxes(tickprefix="$", separatethousands=True)
plotly(fig1)

# 📈 Funding Trends Over Time
text("## 📈 Funding Trends Over Time")
df_trend = df.groupby(["year", "industry"], as_index=False)["amount_million"].sum()
fig2 = px.line(
    df_trend,
    x="year",
    y="amount_million",
    color="industry",
    markers=True,
    title="Annual Funding by Industry",
    labels={"amount_million": "Funding (in $M)"},
    color_discrete_sequence=px.colors.qualitative.Safe,
)
fig2.update_layout(template="plotly_white", title_x=0.5)
fig2.update_yaxes(tickprefix="$", separatethousands=True)
plotly(fig2)

# 🌀 Funding Round Distribution
text("## 🌀 Funding Rounds Distribution")
fig3 = px.pie(
    df,
    names="round",
    values="amount_million",
    title="Distribution of Funding Rounds",
    color_discrete_sequence=px.colors.qualitative.Safe,
)
fig3.update_traces(textinfo="percent+label")
plotly(fig3)
