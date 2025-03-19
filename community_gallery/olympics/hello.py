from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

# Kaggle Dataset - Olympic Medal List (1896-2024)
# https://www.kaggle.com/datasets/amanrajput16/olympics-medal-list-1896-2024?resource=download

text("# Rahul Trivedi - Preswald Coding Assessment")
text("## This app displays information about the Olympic Games from 1896 to 2024")


# STEP - 1: Load the dataset
connect()  # load in all sources, which by default is the sample_csv
df = get_df("sample_csv")

# STEP - 2: Query or manipulate the data

# Query 1 - USA's Olympic Perfomance
sql_1 = "SELECT * FROM sample_csv WHERE NOC = 'United States'"
filtered_df_1 = query(sql_1, "sample_csv")

# STEP - 3: Build an interactive UI
table(filtered_df_1, title="1. USA Ranking & Medal Tally In Every Olympics")

# Query 2 - Top Ranked Country In Each Olympics
sql_2 = "SELECT * FROM sample_csv WHERE Rank = '1'"
filtered_df_2 = query(sql_2, "sample_csv")

# STEP - 3: Build an interactive UI
table(filtered_df_2, title="2. Top Ranked Country In Every Olympics")

# STEP - 3.1: Add user controls
text(
    "Dynamic Data View - Move the slider to filter countries by gold medals. Only countries with at least the selected count of gold medals will be shown"
)
threshold = slider("Threshold", min_val=10, max_val=82, default=46)
table(
    df[df["Gold"] >= threshold],
    title="Countries with Gold Medals Based on Slider Value",
)

# STEP - 4: Create a visualization
text("## Analytics & Visualization")

# Visualization 1 - Create a scatter plot for NOC vs Gold
fig = px.scatter(
    df,
    x="NOC",
    y="Gold",
    text="Year",
    title="Country v/s Gold",
    labels={"Country": "Country", "Gold": "Gold"},
)

# Add labels for each point
fig.update_traces(textposition="top center", marker=dict(size=10, color="lightblue"))

# Style the plot
fig.update_layout(template="plotly_white")

# Show the plot
plotly(fig)

# Visualization 2 - Create a scatter plot for NOC vs Total
fig = px.scatter(
    df,
    x="NOC",
    y="Total",
    text="Year",
    title="Country v/s Total",
    labels={"Country": "Country", "Total": "Total"},
)

# Add labels for each point
fig.update_traces(textposition="top center", marker=dict(size=10, color="lightblue"))

# Style the plot
fig.update_layout(template="plotly_white")

# Show the plot
plotly(fig)

# Show the complete data
table(df, title="Complete Olympics Data (1896 - 2024)")
