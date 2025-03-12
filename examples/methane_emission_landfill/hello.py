from preswald import connect, get_df, query, table, text, plotly, slider, selectbox
import plotly.express as px

# Use connect to initialize the connection
connect()

# Load the dataset  that is stored in the data folder with the name data.csv
df = get_df("data")

# While plotting the data, in order to avoid the JSON serialization problem we change the type of Date to string
df["Observation Date"] = df["Observation Date"].astype(str)

# Below is the title of my visualization project and the guidelines to filter the data using the filters provided
text("# 🏭 Methane Emissions Explorer")
text("""

Explore landfill methane emissions data interactively:

1. **Select a Landfill** to analyze the methane emissions for each landfill.

2. **Apply Filters** to streamline the data. The two filters used are selection of the landmine and the threshold of uncertainty in the source selection.

3. **Visualize** the trends of the emissions extracted from this data which includes the .

""")

# Selectbox is provided in order to select the landfill using the GHGRP ID
text("## Step 1: Select Filters")
selected_landfill = selectbox("Select Landfill (GHGRP ID)", options=df["GHGRP ID"].unique().tolist())

# The threshold slider is created using minimum and maximum values of Emission Uncertainty
uncertainty_threshold = slider(
    "Select Maximum Emission Uncertainty (kg/h)", 
    min(df["Average Landfill Point Source Emission Uncertainty (kg/h)"]), 
    max(df["Average Landfill Point Source Emission Uncertainty (kg/h)"]), 
    0.1  # Step size
)

# SQL query based on selected landfill and uncertainty threshold
sql = f"""
SELECT * FROM data 
WHERE "GHGRP ID" = '{selected_landfill}' 
AND "Average Landfill Point Source Emission Uncertainty (kg/h)" <= {uncertainty_threshold}
"""

filtered_df = query(sql, "data")

# Check if the query returned data
if filtered_df is None or filtered_df.empty:
    text("No data found for the selected landfill with the given filters.")
else:
    # Ensure Observation Date is string in filtered results
    filtered_df["Observation Date"] = filtered_df["Observation Date"].astype(str)

    # Handle NaN values in 'Instantaneous Emission Rate (kg/h)'
    filtered_df["Instantaneous Emission Rate (kg/h)"] = filtered_df["Instantaneous Emission Rate (kg/h)"].fillna(0)

    # Display Table
    text("## Step 2: Filtered Emissions Data")
    table(filtered_df[["Observation Date", "Average Landfill Point Source Emission (kg/h)", "Latitude of Plume Origin", "Longitude of Plume Origin"]])

    # Determine map center and zoom dynamically
    if not filtered_df.empty:
        lat_center = filtered_df["Latitude of Plume Origin"].mean()
        lon_center = filtered_df["Longitude of Plume Origin"].mean()
        zoom_level = 12 if len(filtered_df) > 1 else 14  # Adjust zoom dynamically

        # Map Visualization
        text("## Step 3: Methane Emissions Map")
        fig_map = px.scatter_mapbox(filtered_df, lat="Latitude of Plume Origin", lon="Longitude of Plume Origin",
                                    size="Instantaneous Emission Rate (kg/h)", hover_name="Plume Candidate ID (UTC time of detection)",
                                    color="Instantaneous Emission Rate (kg/h)",
                                    mapbox_style="carto-positron", zoom=zoom_level, center={"lat": lat_center, "lon": lon_center},
                                    title=f"🌍 Methane Emission Sources for Landfill {selected_landfill}")
        plotly(fig_map)

    # **1. Uncertainty vs. Emission Rate Scatter Plot (without trendline)**
    text("## Step 4: Uncertainty vs. Emission Rate")
    fig_uncertainty = px.scatter(filtered_df, x="Instantaneous Emission Rate (kg/h)", y="Instantaneous Emission Rate Uncertainty (kg/h)",
                                 title="📊 Uncertainty vs. Emission Rate",
                                 labels={"Instantaneous Emission Rate (kg/h)": "Emission Rate (kg/h)", "Instantaneous Emission Rate Uncertainty (kg/h)": "Uncertainty (kg/h)"})
    plotly(fig_uncertainty)

    # **2. Emission Rate Distribution Histogram**
    text("## Step 5: Emission Rate Distribution")
    fig_hist = px.histogram(filtered_df, x="Instantaneous Emission Rate (kg/h)", nbins=30,
                            title="📊 Distribution of Instantaneous Emission Rates",
                            labels={"Instantaneous Emission Rate (kg/h)": "Emission Rate (kg/h)"})
    plotly(fig_hist)

    # **3. Emission Trends Over Time**
    text("## Step 6: Emission Trends Over Time")
    fig_trend = px.line(filtered_df, x="Observation Date", y="Average Landfill Point Source Emission (kg/h)",
                        title="📈 Emission Trends Over Time", markers=True)
    plotly(fig_trend)

