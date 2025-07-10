from preswald import connect, get_df, query, text, table, slider, plotly
import plotly.express as px

# Initialize connection to preswald.toml data sources
connect()

# Load data
df = get_df("frax_assets")

# Display header
text("# Frax Balance Sheet Analysis")
text("## Overview")

# Display total assets
total_assets = df["value"].sum()
text(f"Total Assets: ${total_assets:,.0f}")

# Query major assets
sql = "SELECT * FROM frax_assets WHERE value > 50000000 ORDER BY value DESC"
filtered_df = query(sql, "frax_assets")
table(filtered_df, title="Major Assets (>$50M)")

# Add interactive controls
text("## Interactive Analysis")
threshold = slider("Asset Value Threshold ($M)", min_val=0, max_val=200, default=50)

# Create dynamic view based on threshold
filtered_by_threshold = df[df["value"] > threshold * 1000000]
if not filtered_by_threshold.empty:
    table(filtered_by_threshold, title="Dynamic Asset View")
    text(f"Found {len(filtered_by_threshold)} assets above ${threshold}M")
else:
    text("No assets found above the threshold")

# Create visualizations
text("## Visualizations")

# Scatter plot showing asset distribution
fig_scatter = px.scatter(
    df,
    x="name",
    y="value",
    title="Asset Distribution",
    labels={"name": "Asset Name", "value": "Value ($)"},
    height=400
)
fig_scatter.update_traces(marker=dict(size=12))
fig_scatter.update_layout(xaxis_tickangle=-45)
plotly(fig_scatter)

# Pie chart showing asset composition
fig_pie = px.pie(
    df,
    values="value",
    names="name",
    title="Asset Composition",
    height=500
)
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
plotly(fig_pie)
