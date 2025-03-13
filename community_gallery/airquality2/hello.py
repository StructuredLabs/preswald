import plotly.express as px

from preswald import connect, get_df, plotly, query, slider, table, text


# Load the dataset
connect()  # Initialize connection
df = get_df("airquality")


# Query: Filter records where 'Data Value' > 10
sql = 'SELECT * FROM airquality WHERE "Data Value" > 10'
filtered_df = query(sql, "airquality")

# Display static filtered table
text("## Filtered Data (Data Value > 10)")
table(filtered_df, title="Filtered Data")

# User Interaction: Add a slider to filter by Data Value
threshold = slider(
    "Filter by Data Value",
    min_val=df["Data Value"].min(),
    max_val=df["Data Value"].max(),
    default=10,
)

# Dynamically filter data based on slider input
filtered_dynamic_df = df[df["Data Value"] > threshold]
table(filtered_dynamic_df, title="Dynamic Data View")

# Create an interactive scatter plot (Air Quality Trend)
fig = px.scatter(
    filtered_dynamic_df,
    x="Time Period",
    y="Data Value",
    color="Name",
    size="Data Value",
    hover_data=["Geo Place Name", "Measure"],
    title="Air Quality & Emissions Over Time",
)

plotly(fig)

# Create another visualization: Emissions by Geographic Area
fig2 = px.bar(
    filtered_dynamic_df,
    x="Geo Place Name",
    y="Data Value",
    color="Measure",
    title="Air Quality Levels by Location",
    labels={"Geo Place Name": "Location", "Data Value": "Pollution Level"},
)

plotly(fig2)
