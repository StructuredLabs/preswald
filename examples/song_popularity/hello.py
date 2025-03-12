from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

dataset = "top_songs"

# Loading Dataset
connect()
df = get_df(dataset)

# Filtering Dataset
sql = "SELECT * FROM top_songs ORDER BY Popularity DESC LIMIT 100"
filtered_df = query(sql, dataset).drop(columns=["Index"])
filtered_df["Length"] = pd.to_numeric(filtered_df["Length"], errors="coerce")

# Title
text("# An In Depth Look At The Top 100 Songs Up To 2019 According To Spotify")
text(
    "## How Do Different Aspects Of Songs Affect Their Popularity? \n Here are several charts exploring how some factors correlate to popularity"
)

# --- Graphs ---

# Genre
fig_genre = px.histogram(
    filtered_df,
    x="Genre",
    y="Popularity",
    title="Genre's Correlation With Popularity",
    labels={"Genre": "Genre", "Popularity": "Sum of Popularity"},
    color="Genre",
)
fig_genre.update_layout(template="plotly_white", yaxis_title="Sum of Popularity")
plotly(fig_genre)

# Year
fig_year = px.bar(
    filtered_df,
    x="Year",
    y="Popularity",
    hover_data=["Title", "Artist"],
    title="Release Year's Correlation With Popularity",
    labels={"Year": "Release Year", "Popularity": "Sum of Popularity"},
    color="Genre",
)
fig_year.update_layout(
    template="plotly_white", xaxis_title="Release Year", yaxis_title="Sum of Popularity"
)
plotly(fig_year)

# BPM
fig_bpm = px.scatter(
    filtered_df,
    x="BPM",
    y="Popularity",
    hover_data=["Title", "Artist", "Year"],
    labels={"BPM": "BPM", "Popularity": "Popularity"},
    title="BPM's Correlation With Popularity",
    color="Genre",
)
fig_bpm.update_layout(template="plotly_white")
plotly(fig_bpm)

# Length
fig_len = px.scatter(
    filtered_df.sort_values(by="Length"),
    x="Length",
    y="Popularity",
    hover_data=["Title", "Artist", "Year"],
    title="Duration's Correlation With Popularity",
    labels={"Length": "Duration In Seconds", "Popularity": "Popularity"},
    color="Genre",
)
fig_len.update_layout(template="plotly_white", xaxis_title="Duration In Seconds")
plotly(fig_len)

# Loudness
fig_loud = px.bar(
    filtered_df,
    x="Loudness",
    y="Popularity",
    hover_data=["Title", "Artist", "Year"],
    title="Noise Level's Correlation With Popularity",
    labels={"Loudness": "Decibel", "Popularity": "Popularity"},
    color="Genre",
)
fig_loud.update_layout(
    template="plotly_white", xaxis_title="Decibel", yaxis_title="Sum of Popularity"
)
plotly(fig_loud)

# Table
text("\n")
text("## Explore The Data For Yourself!")

threshold = slider(
    "Filter Out Songs By Minimum Release Year", min_val=1967, max_val=2019, default=1967
)

table(filtered_df[filtered_df["Year"] >= threshold], title="Dynamic Table View")
