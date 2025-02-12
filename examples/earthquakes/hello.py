import pandas as pd
import plotly.express as px

from preswald import connect, get_df, plotly, slider, text, view


# Title
text("# Earthquake Analytics Dashboard 🌍")

# Load and connect data
connect()

# Slider for filtering magnitude
min_magnitude = slider("Minimum Magnitude", min_val=0.0, max_val=10.0, default=5.0)

# Read the data and filter based on magnitude
data = get_df("earthquake_data")
# data = get_df("earthquake_db", "earthquake_data") # NOTE: requires changing the column names based on what you have in postgres
# Convert Magnitude column to numeric, handling any non-numeric values
data["Magnitude"] = pd.to_numeric(data["Magnitude"], errors="coerce")
filtered_data = data[data["Magnitude"] >= min_magnitude]

# View the filtered data
view(filtered_data)

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
    filtered_data, x="Magnitude", nbins=20, title="Distribution of Magnitudes"
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
