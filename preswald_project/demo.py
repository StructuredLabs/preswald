from preswald import text, connect, view, slider, plotly, connections
import pandas as pd
import plotly.express as px

# Title
text("# Earthquake Analytics Dashboard 🌍")

# Load and connect data
connection_name = connect("earthquake_data.csv", "earthquake_connection")

# Slider for filtering magnitude
# here min_magnitude is {'type': 'slider', 'id': 'slider-f6dab796', 'label': 'Minimum Magnitude', 'min': 0.0, 'max': 10.0, 'step': 1, 'value': 5.0}
min_magnitude = slider("Minimum Magnitude", min_val=0.0,
                       max_val=10.0, default=5.0)

# Read the data and filter based on magnitude
data = pd.DataFrame(connections[connection_name])
# Convert Magnitude column to numeric, handling any non-numeric values
data['Magnitude'] = pd.to_numeric(data['Magnitude'], errors='coerce')
filtered_data = data[data['Magnitude'] >= min_magnitude.get('value', min_magnitude)]

# Summary statistics
text(f"### Total Earthquakes with Magnitude ≥ {min_magnitude.get('value', min_magnitude)}: {len(filtered_data)}")

# Interactive map using Plotly
text("## Earthquake Locations")
fig_map = px.scatter_geo(
    filtered_data,
    lat='Latitude',
    lon='Longitude',
    color='Magnitude',
    size='Magnitude',
    hover_name='ID',
    title="Earthquake Map"
)
plotly(fig_map)

# Magnitude distribution
text("## Magnitude Distribution")
fig_hist = px.histogram(
    filtered_data,
    x="Magnitude",
    nbins=20,
    title="Distribution of Magnitudes"
)
plotly(fig_hist)

# Depth vs. Magnitude scatter plot
text("## Depth vs. Magnitude")
fig_scatter = px.scatter(
    filtered_data,
    x="Depth",
    y="Magnitude",
    color="Magnitude",
    title="Depth vs Magnitude",
    labels={"Depth": "Depth (km)", "Magnitude": "Magnitude"}
)
plotly(fig_scatter)

# Top earthquakes table
text("## Top 10 Earthquakes by Magnitude")
top_earthquakes = filtered_data.nlargest(10, 'Magnitude')
view("earthquake_connection", limit=10)

# Data table
text("## Filtered Data Table")
view("earthquake_connection")
