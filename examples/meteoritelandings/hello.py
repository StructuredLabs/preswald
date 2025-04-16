# hello.py

"""
Meteorite Landings Analysis App using Preswald
--------------------------------------------------

This app loads a meteorite landings dataset from data/sample.csv and provides
an extensive, interactive analysis including descriptive statistics, dynamic filtering,
and multiple visualizations.

Dataset Columns:
  - name: Name of the meteorite
  - id: Meteorite identifier
  - nametype: Validity of the meteorite
  - recclass: Meteorite classification
  - mass: Mass (in grams)
  - fall: Indicates whether the meteorite "Fell" or was "Found"
  - year: Year of the meteorite landing
  - reclat: Latitude
  - reclong: Longitude
  - GeoLocation: String representation of (reclat, reclong)
"""

#############################################
# 1) LOAD AND PREPARE THE DATASET
#############################################

from preswald import connect, get_df, query, table, text, slider, plotly
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import datetime

# Initialize connection to data sources from preswald.toml
connect()

# Load the dataset using the key "sample_csv"
df = get_df("sample_csv")

# Debug prints (optional)
# print("Columns:", df.columns)
# print(df.head())

# Convert "Draw Date" to datetime for proper time-series plotting.
# Note: In this meteorite dataset, we may not have a "Draw Date".
# Instead, we will use the "year" column to create a datetime representation.
# We'll create a new column "year_dt" from "year".

def parse_year(val):
    try:
        if isinstance(val, str):
            # Some values might include extra characters or be in ISO format.
            return pd.to_datetime(val, errors="coerce")
        elif isinstance(val, (int, float)):
            return pd.to_datetime(str(int(val)), format="%Y", errors="coerce")
        else:
            return pd.NaT
    except Exception as e:
        return pd.NaT

df["year_dt"] = df["year"].apply(parse_year)

# Convert "mass" to numeric (in grams); handle missing or mis-formatted values.
df["mass"] = pd.to_numeric(df["mass"], errors="coerce")

# Ensure reclat and reclong are numeric.
df["reclat"] = pd.to_numeric(df["reclat"], errors="coerce")
df["reclong"] = pd.to_numeric(df["reclong"], errors="coerce")

# Drop rows with missing essential data: mass, year_dt, reclat, reclong
df = df.dropna(subset=["mass", "year_dt", "reclat", "reclong"])

#############################################
# 2) DESCRIPTIVE STATISTICS & DATA EXPLORATION
#############################################

# Calculate basic descriptive statistics for mass and year.
mass_mean = df["mass"].mean()
mass_median = df["mass"].median()
mass_std = df["mass"].std()

year_min = df["year_dt"].min()
year_max = df["year_dt"].max()

# Prepare a dictionary with summary statistics.
stats_summary = {
    "Mass Mean (g)": mass_mean,
    "Mass Median (g)": mass_median,
    "Mass Std Dev (g)": mass_std,
    "Earliest Year": year_min.strftime("%Y") if pd.notnull(year_min) else "N/A",
    "Latest Year": year_max.strftime("%Y") if pd.notnull(year_max) else "N/A",
    "Total Records": len(df)
}

def stats_to_df(stats):
    data = [{"Statistic": k, "Value": v} for k, v in stats.items()]
    return pd.DataFrame(data)

stats_df = stats_to_df(stats_summary)

#############################################
# 3) DATA QUERY USING PRESWALD QUERY
#############################################

# For demonstration, filter meteorites with mass greater than 10000 g.
# (The original requirement "value > 50" is adapted here to "mass > 10000" since our dataset is different.)
sql_query = 'SELECT * FROM sample_csv WHERE "mass" > 10000'
try:
    heavy_meteorites = query(sql_query, "sample_csv")
except Exception as e:
    heavy_meteorites = df[df["mass"] > 10000]

#############################################
# 4) BUILD THE INTERACTIVE UI
#############################################

# Display the title and introduction.
text("# Meteorite Landings Analysis")
text("Explore an extensive interactive analysis of meteorite landings data with dynamic filters and visualizations.")
text("This app provides descriptive statistics, dynamic filtering, and multiple chart types for in-depth exploration.")

# Display descriptive statistics.
table(stats_df, title="Dataset Descriptive Statistics")

# Display the heavy meteorites table.
table(heavy_meteorites, title="Meteorites with Mass > 10,000 g")

#############################################
# 5) ADD USER CONTROLS FOR DYNAMIC FILTERING
#############################################

# Create a slider for dynamic filtering by mass.
mass_min = float(df["mass"].min())
mass_max = float(df["mass"].max())
mass_threshold = slider("Mass Threshold (g)", min_val=mass_min, max_val=mass_max, default=10000)

# Create a slider for filtering by year using the year component of "year_dt".
min_year = int(df["year_dt"].dt.year.min())
max_year = int(df["year_dt"].dt.year.max())
year_threshold = slider("Minimum Year", min_val=min_year, max_val=max_year, default=min_year)

# Filter dataset dynamically based on slider values.
filtered_dynamic = df[(df["mass"] > mass_threshold) & (df["year_dt"].dt.year >= year_threshold)]
table(filtered_dynamic, title=f"Dynamic Data View (Mass > {mass_threshold:.0f} g and Year >= {year_threshold})")

#############################################
# 6) VISUALIZATIONS
#############################################

# 6a) Scatter Plot: Meteorite Mass vs. Year (using logarithmic scale for mass)
fig_scatter = px.scatter(
    df,
    x=df["year_dt"].dt.year,
    y="mass",
    color="mass",
    title="Meteorite Mass vs. Year (Log Scale)",
    labels={"x": "Year", "mass": "Mass (g)"},
    log_y=True,
    hover_data=["name", "recclass"]
)
plotly(fig_scatter)

# 6b) Bar Chart: Top 10 Meteorite Recclass by Frequency
recclass_counts = df["recclass"].value_counts().nlargest(10).reset_index()
recclass_counts.columns = ["recclass", "count"]
fig_bar = px.bar(
    recclass_counts,
    x="recclass",
    y="count",
    title="Top 10 Meteorite Recclass by Frequency",
    labels={"recclass": "Meteorite Recclass", "count": "Frequency"}
)
plotly(fig_bar)

# 6c) Geo-Map: Meteorite Landing Locations
fig_map = px.scatter_geo(
    df,
    lat="reclat",
    lon="reclong",
    color="mass",
    hover_name="name",
    size="mass",
    projection="natural earth",
    title="Meteorite Landing Locations"
)
plotly(fig_map)

# 6d) Time Series: Total Meteorite Mass per Decade
df["decade"] = (df["year_dt"].dt.year // 10) * 10
decade_mass = df.groupby("decade")["mass"].sum().reset_index()
fig_line = px.line(
    decade_mass,
    x="decade",
    y="mass",
    title="Total Meteorite Mass per Decade",
    labels={"decade": "Decade", "mass": "Total Mass (g)"}
)
plotly(fig_line)

# 6e) Box Plot: Mass Distribution by Fall Type
fig_box = px.box(
    df,
    x="fall",
    y="mass",
    title="Mass Distribution by Fall Type",
    labels={"fall": "Fall Type", "mass": "Mass (g)"},
    log_y=True
)
plotly(fig_box)

#############################################
# 7) ADVANCED ANALYSIS AND CUSTOM VISUALIZATIONS
#############################################

# 7a) Average Meteorite Mass by Recclass (for recclasses with more than 20 records)
recclass_avg = df.groupby("recclass")["mass"].agg(["mean", "count"]).reset_index()
recclass_avg = recclass_avg[recclass_avg["count"] > 20].sort_values(by="mean", ascending=False)
fig_recclass = px.bar(
    recclass_avg,
    x="recclass",
    y="mean",
    title="Average Meteorite Mass by Recclass (Classes with > 20 Records)",
    labels={"recclass": "Recclass", "mean": "Average Mass (g)"}
)
plotly(fig_recclass)

# 7b) Area Chart: Meteorite Fall Frequency Over Time (Fell vs. Found)
df["fall_year"] = df["year_dt"].dt.year.astype(int)
fall_counts = df.groupby(["fall", "fall_year"]).size().reset_index(name="count")
fig_area = px.area(
    fall_counts,
    x="fall_year",
    y="count",
    color="fall",
    title="Meteorite Fall Frequency Over Time",
    labels={"fall_year": "Year", "count": "Number of Meteorites", "fall": "Fall Type"}
)
plotly(fig_area)

# 7c) Custom Analysis for Selected Recclass
def analyze_recclass(recclass_choice):
    subset = df[df["recclass"] == recclass_choice]
    avg_mass = subset["mass"].mean()
    total_mass = subset["mass"].sum()
    count = len(subset)
    return subset, avg_mass, total_mass, count

# For demonstration, select the recclass with the highest average mass from recclass_avg if available.
if not recclass_avg.empty:
    selected_recclass = recclass_avg.iloc[0]["recclass"]
else:
    selected_recclass = "Unknown"

subset_recclass, avg_mass_recclass, total_mass_recclass, count_recclass = analyze_recclass(selected_recclass)

# Display the custom analysis results.
text(f"### Analysis for Recclass: {selected_recclass}")
text(f"Average Mass: {avg_mass_recclass:.2f} g")
text(f"Total Mass: {total_mass_recclass:.2f} g")
text(f"Total Count: {count_recclass}")

# Show a table with data for the selected recclass.
table(subset_recclass, title=f"Data for Recclass: {selected_recclass}")

# Scatter plot for the selected recclass: Mass vs. Year.
fig_recclass_scatter = px.scatter(
    subset_recclass,
    x=subset_recclass["year_dt"].dt.year,
    y="mass",
    title=f"Meteorite Mass Over Time for Recclass {selected_recclass}",
    labels={"x": "Year", "mass": "Mass (g)"},
    log_y=True,
    hover_data=["name"]
)
plotly(fig_recclass_scatter)

#############################################
# 8) ADDITIONAL INTERACTIVE ELEMENTS
#############################################

# Dynamic update function for mass filtering.
def update_dynamic_view(mass_limit):
    dynamic_view = df[df["mass"] > mass_limit]
    table(dynamic_view, title=f"Dynamic View: Meteorites with Mass > {mass_limit:.0f} g")

# Another slider for dynamic mass filtering demonstration.
mass_slider = slider("Dynamic Mass Filter", min_val=mass_min, max_val=mass_max, default=5000)
update_dynamic_view(mass_slider)

# Additional control: a slider for filtering by reclat (latitude).
lat_min = float(df["reclat"].min())
lat_max = float(df["reclat"].max())
lat_threshold = slider("Minimum Latitude", min_val=lat_min, max_val=lat_max, default=lat_min)
filtered_by_lat = df[df["reclat"] >= lat_threshold]
table(filtered_by_lat, title=f"Meteorites with Latitude >= {lat_threshold:.2f}")

#############################################
# 9) MULTIPLE VISUALIZATION COMPARISONS
#############################################

# 9a) Compare mass distribution across different recclasses using a violin plot.
fig_violin = px.violin(
    df,
    x="recclass",
    y="mass",
    title="Mass Distribution across Recclasses",
    box=True,
    points="all",
    log_y=True
)
fig_violin.update_layout(xaxis={'categoryorder':'total descending'})
plotly(fig_violin)

# 9b) Create a histogram for the mass of meteorites.
fig_hist = px.histogram(
    df,
    x="mass",
    nbins=50,
    title="Histogram of Meteorite Masses",
    labels={"mass": "Mass (g)"}
)
fig_hist.update_xaxes(type="log")
plotly(fig_hist)

# 9c) Create a bubble chart: x = reclong, y = reclat, bubble size = mass, color = year.
fig_bubble = px.scatter(
    df,
    x="reclong",
    y="reclat",
    size="mass",
    color=df["year_dt"].dt.year.astype(str),
    title="Meteorite Landings: Bubble Chart by Location",
    labels={"reclong": "Longitude", "reclat": "Latitude", "color": "Year"}
)
plotly(fig_bubble)

#############################################
# 10) FINAL SUMMARY & CONCLUSIONS
#############################################

text("## Summary and Conclusions")
text("This interactive Preswald app provides a multifaceted analysis of the meteorite landings dataset.")
text("Key features include:")
text("- Descriptive statistics and summary tables.")
text("- Dynamic filtering via sliders for mass, year, and latitude.")
text("- Multiple visualizations: scatter plots, bar charts, geo-maps, area charts, violin plots, histograms, and bubble charts.")
text("- Custom analysis for specific meteorite recclasses.")
text("Experiment with the controls to discover insights about meteorite distributions, trends over time, and regional variations.")
text("Thank you for exploring the Meteorite Landings Analysis App!")

#############################################
# END OF APP
#############################################
