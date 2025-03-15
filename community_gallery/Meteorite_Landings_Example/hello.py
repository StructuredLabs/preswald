from preswald import text, plotly, connect, get_df, table, slider , query
import pandas as pd
import plotly.express as px

# App Title
text("# ☄️ Meteorite Landings Analysis")
text("Explore thousands of meteorites that have fallen to Earth!")

# Load the CSV
connect() 
df = get_df('Meteorite_Landings_csv')

# Convert columns to appropriate types
df["mass (g)"] = pd.to_numeric(df["mass (g)"], errors="coerce")  # Convert mass to numeric
df["year"] = pd.to_datetime(df["year"], errors="coerce").dt.year  # Extract year
df = df.dropna(subset=["reclat", "reclong", "mass (g)", "year"])  # Remove rows with missing data

# Slider for selecting minimum meteorite mass
min_mass = slider("Select Minimum Meteorite Mass (grams)", min_val=0, max_val=50000, default=1000)

# SQL Query: Filter meteorites based on the selected minimum mass
sql_query_filtered = f'SELECT * FROM Meteorite_Landings_csv WHERE "mass (g)" > {min_mass}'
filtered_df = query(sql_query_filtered, "Meteorite_Landings_csv")

# Get Top 10 Heaviest Meteorites
sql_query_top10 = 'SELECT name, "mass (g)" FROM Meteorite_Landings_csv ORDER BY "mass (g)" DESC LIMIT 10'
top_10_df = query(sql_query_top10, "Meteorite_Landings_csv")

# Get Meteorite Landings Per Year**
sql_query_yearly = "SELECT year, COUNT(*) as count FROM Meteorite_Landings_csv GROUP BY year ORDER BY year"
yearly_df = query(sql_query_yearly, "Meteorite_Landings_csv")

# Display Filtered Data Table
table(filtered_df, title=f"Meteorites with Mass > {min_mass}g")

# Scatter Plot (Meteorite Locations)
fig = px.scatter_geo(
    filtered_df,
    lat="reclat",
    lon="reclong",
    size="mass (g)",
    color="mass (g)",
    hover_name="name",
    hover_data=["year", "mass (g)"],
    projection="natural earth",
    title="🌍 Meteorite Landings Across the Globe"
)
plotly(fig)

# Bar Chart: Top 10 Heaviest Meteorites
fig_bar = px.bar(
    top_10_df,
    x="name",
    y="mass (g)",
    color="mass (g)",
    title="💥 Top 10 Heaviest Meteorites",
    labels={"name": "Meteorite Name", "mass (g)": "Mass (grams)"}
)
plotly(fig_bar)

# Line Chart: Meteorite Landings Over Time
fig_line = px.line(
    yearly_df,
    x="year",
    y="count",
    title="📆 Meteorite Landings Over Time",
    labels={"year": "Year", "count": "Number of Landings"},
    markers=True
)
plotly(fig_line)