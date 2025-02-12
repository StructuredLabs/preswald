import pandas as pd
import plotly.express as px

from preswald import plotly, text


# Display the dashboard title
text("# Fire Incident Analytics Dashboard 🔥")

# Connect to the data

# Load and preprocess the data
data = pd.read_csv("mapdataall.csv")
data["incident_acres_burned"] = pd.to_numeric(
    data["incident_acres_burned"], errors="coerce"
)

# Ensure the 'incident_dateonly_created' column is in datetime format
data["incident_dateonly_created"] = pd.to_datetime(
    data["incident_dateonly_created"], errors="coerce"
)

# Filter data for Los Angeles County in 2025
filtered_data = data[
    (data["incident_county"] == "Los Angeles")
    & (data["incident_dateonly_created"].dt.year == 2025)
]

# Add a new subsection for LA fires in 2025 (Scatter Map)
text("## Los Angeles Fires in 2025 Map")
fig_map = px.scatter_mapbox(
    filtered_data,
    lat="incident_latitude",
    lon="incident_longitude",
    hover_name="incident_name",
    hover_data=["incident_acres_burned", "incident_containment"],
    color="incident_acres_burned",
    size="incident_acres_burned",
    zoom=8,
    mapbox_style="open-street-map",
    title="Los Angeles Fires in 2025",
)

# Update marker properties for better visibility
fig_map.update_traces(
    marker={
        "size": 20,  # Increase marker size
        "opacity": 0.9,  # Slightly transparent
        "symbol": "circle",  # Set symbol type
    }
)

# Display the Scatter Map
plotly(fig_map)

# Add a Bar Chart for Acres Burned and Containment
text("## Acres Burned and Containment Bar Chart")
fig_bar = px.bar(
    filtered_data.sort_values(by="incident_acres_burned", ascending=False),
    x="incident_name",  # Use fire names as categories
    y="incident_acres_burned",
    color="incident_containment",
    title="Acres Burned and Containment",
    labels={
        "incident_acres_burned": "Acres Burned",
        "incident_containment": "Containment (%)",
        "incident_name": "Fire Name",
    },
    hover_data=["incident_acres_burned", "incident_containment"],
)

# Scale down the bar chart
fig_bar.update_layout(
    xaxis_tickangle=45,  # Rotate x-axis labels for better readability
    height=500,  # Scale down the figure height
    title_x=0.5,  # Center the title
)

# Display the Bar Chart
plotly(fig_bar)

# Add a Line Chart for Fire Trends Over Time (Filtered for 2000s and Later)
text("## Fire Trends Over Time")

# Ensure there are valid dates and filter for data from 2000 onwards
# Filter for 2000 and later
data = data[data["incident_dateonly_created"].dt.year >= 2000]
data["incident_month"] = data["incident_dateonly_created"].dt.to_period("M").astype(str)

# Group by month
trend_data = data.groupby("incident_month", as_index=False).agg(
    {
        "incident_acres_burned": "sum",  # Total acres burned per month
        # Number of incidents per month
        "incident_id": "count" if "incident_id" in data.columns else None,
    }
)

# Check if trend_data has values
if not trend_data.empty:
    fig_line = px.line(
        trend_data,
        x="incident_month",
        y="incident_acres_burned",
        title="Fire Trends Over Time (2000 to Present)",
        labels={
            "incident_month": "Month",
            "incident_acres_burned": "Total Acres Burned",
        },
        markers=True,
    )

    fig_line.update_traces(
        line={"width": 3}, marker={"size": 8}
    )  # Enhance line and marker visibility
    fig_line.update_layout(
        xaxis_title="Month",
        yaxis_title="Total Acres Burned",
        xaxis_tickangle=45,  # Rotate x-axis labels for readability
        height=500,  # Adjust the height for a cleaner display
    )
    plotly(fig_line)
else:
    text("### No data available for the Fire Trends Over Time chart.")
