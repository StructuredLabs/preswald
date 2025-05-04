from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import plotly.express as px


text("# Water Consumption Analysis App")
# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')


from preswald import query
sql = "SELECT * FROM my_dataset WHERE [Per Capita Water Use (Liters per Day)] > 50"
filtered_df = query(sql, "my_dataset")

# display the filtered data


table(filtered_df, title="Filtered Data")

# user controls to dynamically filter data

# User control: Slider to dynamically filter by Per Capita Water Use
threshold = slider("Threshold (Liters per Day)", min_val=0, max_val=100, default=50)
table(
    df[df["Per Capita Water Use (Liters per Day)"] > threshold],
    title="Data View (Filtered by Threshold)"
)

# Slider to filter data by Year
year = slider("Select Year", min_val=2000, max_val=2024, default=2020)
year_df = df[df["Year"] == year]
table(year_df, title=f"Data for Year {year}")

# 5. Create a visualization

fig = px.scatter(
    df,
    x="Total Water Consumption (Billion Cubic Meters)",
    y="Rainfall Impact (Annual Precipitation in mm)",
    color="Water Scarcity Level",
    hover_data=["Country", "Year"]
)
plotly(fig)

# Stacked Bar Chart for average water usage by sector across scarcity levels
sector_cols = ["Agricultural Water Use (%)", "Industrial Water Use (%)", "Household Water Use (%)"]
agg_df = df.groupby("Water Scarcity Level")[sector_cols].mean().reset_index()
melted_df = agg_df.melt(
    id_vars="Water Scarcity Level",
    var_name="Sector",
    value_name="Average Use (%)"
)
fig2 = px.bar(
    melted_df,
    x="Water Scarcity Level",
    y="Average Use (%)",
    color="Sector",
    title="Average Water Use by Sector across Scarcity Levels",
    barmode="stack"
)
plotly(fig2)