import pandas as pd
import plotly.express as px

from preswald import connect, get_df, plotly, slider, table, text

# Title
text("# Earthquake Analytics Dashboard 🌍")

# Load and connect data
connect()

# ---

# Clickhouse section

query_string = """
WITH yearly_stats AS
    (
        SELECT
            toYear(Date) AS year,
            count() AS earthquake_count,
            round(avg(Magnitude), 2) AS avg_magnitude,
            round(max(Magnitude), 2) AS max_magnitude,
            round(avg(Depth), 2) AS avg_depth,
            countIf(Magnitude >= 6.) AS significant_quakes
        FROM earthquakes
        WHERE toYear(Date) >= 1970
        GROUP BY year
        ORDER BY year DESC
    )
SELECT
    current.year,
    current.earthquake_count,
    current.avg_magnitude,
    current.max_magnitude,
    current.avg_depth,
    current.significant_quakes,
    round(((current.earthquake_count - previous.earthquake_count) / previous.earthquake_count) * 100, 1) AS yoy_change_percent
FROM yearly_stats AS current
LEFT JOIN yearly_stats AS previous
    ON current.year = previous.year + 1
ORDER BY current.year DESC
LIMIT 10
"""

# c_data = query("SELECT * FROM earthquakes LIMIT 50;", "eq_clickhouse")
# d_data = query(query_string, "eq_clickhouse")

# table(c_data)
# table(d_data)

# ---

# Slider for filtering magnitude
min_magnitude = slider("Minimum Magnitude", min_val=0.0, max_val=10.0, default=5.0)

# Read the data and filter based on magnitude
data = get_df("earthquake_data")
# data = get_df("earthquake_db", "earthquake_data") # NOTE: requires changing the column names based on what you have in postgres
data["Magnitude"] = pd.to_numeric(data["Magnitude"], errors="coerce")
filtered_data = data[data["Magnitude"] >= min_magnitude]

# View the filtered data
table(filtered_data)

# Summary statistics
text(f"### Total Earthquakes with Magnitude ≥ {min_magnitude}: {len(filtered_data)}")

# Interactive map using Plotly
text("## Earthquake Locations")
fig_map = px.scatter_geo(
    filtered_data,
    lat="Latitude",
    lon="Longitude",
    color="Magnitude",
    size="Magnitude",
    hover_name="ID",
    title="Earthquake Map",
)
plotly(fig_map)

# Magnitude distribution
fig_hist = px.histogram(
    filtered_data,
    x="Magnitude",
    nbins=20,
    title="Distribution of Magnitudes"
)
fig_hist.update_layout(  # 🆕 Add x/y axis labels
    xaxis_title="Magnitude",
    yaxis_title="Number of Earthquakes"
)
plotly(fig_hist)

# Depth vs. Magnitude scatter plot
fig_scatter = px.scatter(
    filtered_data,
    x="Depth",
    y="Magnitude",
    color="Magnitude",
    title="Depth vs Magnitude",
    labels={"Depth": "Depth (km)", "Magnitude": "Magnitude"},
)
plotly(fig_scatter)
