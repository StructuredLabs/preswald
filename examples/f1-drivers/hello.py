import plotly.express as px

from preswald import connect, get_df, plotly, slider, table, text


text("# Formula 1 Driver Analysis !")

# Load the Driver data CSV
connect()
drivers_df = get_df("drivers_csv")

# (1) Analyze Nationality

# Group by nationality
driver_nationality = (
    drivers_df.groupby("nationality")["nationality"]
    .count()
    .sort_values(ascending=False)
    .reset_index(name="number of drivers")
)

# Visualize data in a Bar chart
text("## Formula 1 - Driver Nationality Analysis - 1950 to 2024")

fig = px.bar(
    driver_nationality, x="nationality", y="number of drivers", text="number of drivers"
)
fig.update_traces(textposition="outside")

# Show the plot
plotly(fig)

# Top N Nationality

# slider to select the number of top nationalities to display
top_n = slider("Select Top N Nationalities", min_val=3, max_val=15, default=10)

# Get the top N values based on slider value
top_nationalities = driver_nationality.head(top_n)

# display table
table(top_nationalities, title=f"Top {top_n} Nationalities in Formula 1 Drivers")

# Visualize Top N driver nationality in a Bar Chart
fig_pie = px.pie(
    top_nationalities,
    names="nationality",
    values="number of drivers",
    title="Formula 1 Driver Nationality Distribution",
)

# Show the plot
plotly(fig_pie)


# (2) DOB analysis

text("## Formula 1 - Drivers Born Per Decade")

# Extract decade
drivers_df["birth_decade"] = (drivers_df["dob"].dt.year // 10) * 10

fig_dob = px.histogram(
    drivers_df,
    x="birth_decade",
    nbins=8,
    labels={"birth_decade": "Birth Decade", "count": "Number of Drivers"},
)

plotly(fig_dob)
