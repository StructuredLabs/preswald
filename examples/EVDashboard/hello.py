import pandas as pd
import plotly.express as px
import re

from preswald import connect, get_df, plotly, slider, table, text

# Title
text("# EV Analytics Dashboard 🚗⚡")

# Load and connect data
connect()

# ---
# Read the EV dataset (Limit the data to a smaller subset for performance)
data = get_df("evdata").sample(1000, random_state=42)  # Randomly sample 1000 rows

# Convert Electric Range column to numeric, handling any non-numeric values
data["Electric Range"] = pd.to_numeric(data["Electric Range"], errors="coerce")

# Extract latitude and longitude from the Vehicle Location column
def extract_lat_lon(point):
    match = re.match(r"POINT \((-?[0-9\.]+) (-?[0-9\.]+)\)", point)
    return (float(match.group(2)), float(match.group(1))) if match else (None, None)

data[["Latitude", "Longitude"]] = data["Vehicle Location"].apply(lambda x: pd.Series(extract_lat_lon(x)))

# Filter data based on minimum electric range
min_range = slider("Minimum Electric Range", min_val=0, max_val=400, default=50)
filtered_data = data[data["Electric Range"] >= min_range]


# Summary statistics
text(f"### Total EVs with Range ≥ {min_range} miles: {len(filtered_data)}")

# EV Registrations Over Time
fig_yearly = px.histogram(
    filtered_data, x="Model Year", title="EV Registrations Over Time")
plotly(fig_yearly)

# EV Type Distribution
fig_ev_type = px.pie(
    filtered_data, names="Electric Vehicle Type", title="EV Type Distribution")
plotly(fig_ev_type)

# Popular EV Manufacturers
fig_makes = px.bar(
    filtered_data.groupby("Make").size().reset_index(name="count"),
    x="Make", y="count", title="Top EV Manufacturers",
    labels={"count": "Number of Vehicles"},
)
plotly(fig_makes)

# Electric Range Distribution
fig_range = px.histogram(
    filtered_data, x="Electric Range", nbins=20, title="Electric Range Distribution")
plotly(fig_range)

# EVs by Location (Map)
fig_map = px.scatter_geo(
    filtered_data,
    lat="Latitude",
    lon="Longitude",
    color="Make",
    hover_name="Model",
    title="EV Distribution by Location",
    scope="usa"
    )
plotly(fig_map)

# Display the filtered data
table(filtered_data)