from preswald import text, plotly, connect, get_df, table, query, selectbox
import pandas as pd
import plotly.express as px

text("# Global Water Consumption Insights 💧📊")


# Load the CSV from Preswald's registered data source
connect()
df = get_df("global_water_consumption")

# Get unique country names
country_list = query(
    "SELECT DISTINCT Country FROM global_water_consumption", "global_water_consumption"
)["Country"].tolist()

# Dropdown for user selection
selected_country = selectbox(
    "Choose a country:", options=country_list, default=country_list[0]
)

selected_year = query(
    "SELECT MAX(Year) as max_year FROM global_water_consumption",
    "global_water_consumption",
)["max_year"][0]


# Filter dataset based on selected country and year
df_filtered = query(
    f"SELECT * FROM global_water_consumption WHERE Country = '{selected_country}' AND Year = {selected_year}",
    "global_water_consumption",
)
table(df_filtered, title="Filtered Water Consumption Data")

# Bar Chart: Total Water Consumption per Country
total_consumption = query(
    "SELECT Country, SUM(total_water_sonsumption_billion_cubic_meters) as Total FROM global_water_consumption GROUP BY Country",
    "global_water_consumption",
)
fig_bar = px.bar(
    total_consumption,
    x="Country",
    y="Total",
    title="Total Water Consumption by Country",
    color="Total",
)
plotly(fig_bar)

trend_data = query(
    f"SELECT Year, total_water_sonsumption_billion_cubic_meters FROM global_water_consumption "
    f"WHERE Country = '{selected_country}'",
    "global_water_consumption",
)

# Check if data is available before plotting
if trend_data is not None and not trend_data.empty:
    # Create a scatter plot
    fig_scatter = px.scatter(
        trend_data,
        x="Year",
        y="total_water_sonsumption_billion_cubic_meters",
        color="total_water_sonsumption_billion_cubic_meters",  # Gradient effect
        color_continuous_scale="Viridis",  # gradient
        title=f"Water Consumption Trends in {selected_country}",
        labels={
            "Year": "Year",
            "total_water_sonsumption_billion_cubic_meters": "Water Consumption (Billion Cubic Meters)",
        },
        size_max=10,  # Control dot size
    )

    # Hide the color bar
    fig_scatter.update_layout(coloraxis_showscale=False)

    # Customize marker style
    fig_scatter.update_traces(
        marker=dict(size=10, opacity=0.8, line=dict(width=1, color="black"))
    )

    # Show the plot
    plotly(fig_scatter)
else:
    text(f"No data available for {selected_country}.")


# Pie Chart: Water Use Distribution
# Query water use data for the selected country
water_use = query(
    f"SELECT Country, SUM(Agricultural_Water_Use) AS Agriculture, "
    f"SUM(Industrial_Water_Use) AS Industry, SUM(Household_Water_Use) AS Household "
    f"FROM global_water_consumption WHERE Country = '{selected_country}' GROUP BY Country",
    "global_water_consumption",
)

# Check if data is available before plotting
if water_use is None or water_use.empty:
    text(f"No water use data found for {selected_country}.")
else:
    # Reshape data for Pie Chart
    water_use_melted = water_use.melt(
        id_vars=["Country"], var_name="Water Use Type", value_name="Usage Percentage"
    )

    # Create Pie Chart
    fig_pie = px.pie(
        water_use_melted,
        values="Usage Percentage",
        names="Water Use Type",
        title=f"Water Use Distribution in {selected_country}",
        color="Water Use Type",
        color_discrete_map={
            "Agriculture": "#1f77b4",
            "Industry": "#ff7f0e",
            "Household": "#2ca02c",
        },
    )

    # Display Pie Chart
    plotly(fig_pie)
