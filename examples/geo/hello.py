import pandas as pd
import plotly.express as px
from preswald import (
    get_df,
    plotly,
    table,
    text,
    slider,
    selectbox,
    sidebar,
    checkbox,
    topbar,
    alert,
    image,
    progress,
    chat,
    separator,
)

# Add sidebar and topbar for structure
sidebar(name="🗺️ Global Monuments Explorer", logo="images/logo.png")
topbar()

# App Header
text("""
# 🏛️ Monument Intelligence Dashboard
Explore historic monuments around the world with dynamic filters, geographic visualizations, and chat-powered analytics.
""")
separator()

# Load data
df = get_df("monuments_geo")

if df is not None:
    df.columns = df.columns.str.lower()

    # Flatten geometry
    df["latitude"] = df["geometry"].apply(lambda g: g.get("coordinates", [None, None])[1])
    df["longitude"] = df["geometry"].apply(lambda g: g.get("coordinates", [None, None])[0])
    df["country"] = df["location"].apply(lambda loc: loc.split(",")[-1].strip())

    # Drop rows with missing lat/lon
    df = df.dropna(subset=["latitude", "longitude"])

    # Summary Stats
    text(f"### 🗂 Total Monuments: **{len(df)}**", size=0.5)
    text(f"### 🌍 Countries Covered: **{df['country'].nunique()}**", size=0.5)
    separator()

    # Filters
    min_visitors = slider("🎟️ Minimum Visitors Per Year", min_val=0, max_val=20000000, default=1000000, step=100000)
    text("")
    year_cutoff = slider("🏗️ Built After Year", min_val=-700, max_val=2025, default=1800)
    text("")
    historic_filter = checkbox("🕰️ Show Ancient Monuments (Before 1000 AD)", default=True)

    # Apply filters
    filtered = df[df["visitors_per_year"] >= min_visitors]
    filtered = filtered[filtered["year_built"] >= year_cutoff]
    if not historic_filter:
        filtered = filtered[filtered["year_built"] >= 1000]

    shown_pct = round(len(filtered) / len(df) * 100, 1)
    progress("📊 Visible Monuments (%)", value=shown_pct)
    alert(f"{len(filtered)} monuments match your filters.", level="info")

    # Table
    text("## 📋 Filtered Monument List")
    table(filtered[["name", "location", "year_built", "visitors_per_year"]].sort_values("visitors_per_year", ascending=False))

    # Map
    separator()
    text("## 🌐 Global Monument Map")

    # Normalize size for better visibility
    filtered["scaled_size"] = pd.qcut(filtered["visitors_per_year"], q=5, labels=[5, 10, 15, 20, 30]).astype(int)

    fig_map = px.scatter_geo(
        filtered,
        lat="latitude",
        lon="longitude",
        size="scaled_size",
        color="country",
        hover_name="name",
        title="Visitor Hotspots Around the Globe",
        projection="natural earth",
    )

    fig_map.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='white')))
    fig_map.update_layout(geo=dict(showland=True, landcolor="LightGray"))
    plotly(fig_map)

    # Country Ranking
    separator()
    text("## 🏳️ Top Countries by Monument Count")
    top_countries = filtered["country"].value_counts().nlargest(8).reset_index()
    top_countries.columns = ["Country", "Count"]
    fig_bar = px.bar(top_countries, x="Country", y="Count", title="Top Countries by Monument Count", text_auto=True, color="Country")
    plotly(fig_bar)

    # Visitors Over Time Chart
    separator()
    text("## 📈 Average Visitors by Build Century")
    filtered["century"] = (filtered["year_built"] // 100 * 100).astype(int)
    century_df = filtered.groupby("century")["visitors_per_year"].mean().reset_index()
    fig_line = px.line(century_df, x="century", y="visitors_per_year", title="Average Visitors Per Century", markers=True)
    plotly(fig_line)

    # Optional image section
    if checkbox("🖼️ Show App Logo"):
        image(src="images/logo.png", alt="Monument Logo", className="rounded-xl shadow-xl")

    # Interactive Chat
    separator()
    text("## 🤖 Ask Questions About the Data")
    chat("monuments_geo")

else:
    alert("🚫 No data available to display.", level="warning")
