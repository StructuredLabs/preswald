import pandas as pd
import plotly.express as px

from preswald import plotly, text

text("# Netflix Movies & TV Shows Dashboard")

# Read the data
data = pd.read_csv("data/netflix_titles.csv")

# Generate pie chart data from raw data based on its type
data_pie = data.groupby("type").size().reset_index(name="count")

# Create pie chart
fig_pie = px.pie(
    data_pie, values="count", names="type", title="Netflix Movies & TV Shows by Type"
)
plotly(fig_pie)

# Generate bar chart data from raw data based on its country
data_bar = data.groupby("country").size().reset_index(name="count")

# Create bar chart
fig_bar = px.bar(
    data_bar, x="country", y="count", title="Netflix Movies & TV Shows by Country"
)
plotly(fig_bar)

# Generate line chart data from raw data based on its release year
data_line = data.groupby("release_year").size().reset_index(name="count")

# Create line chart
fig_line = px.line(
    data_line,
    x="release_year",
    y="count",
    title="Netflix Movies & TV Shows by Release Year",
)
plotly(fig_line)
