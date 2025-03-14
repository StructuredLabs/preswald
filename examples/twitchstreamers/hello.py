from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')

print(df.columns)

# Filter out everyone with less than 3 mil subs
sql = "SELECT * FROM sample_csv WHERE Followers > 3000000 "
filtered_df = query (sql, "sample_csv")

# Build an Interactive UI
text("# Twitch Streamers Analysis App")
table(filtered_df, title="Followers > 3000000")

threshold = slider("Average Viewers", min_val=20000, max_val=50000, default=30000)
table(filtered_df[filtered_df["Average viewers"] > threshold], title="Dynamic Viewer Data")

# Shows relation between stream time and followers gained
fig = px.scatter(filtered_df, x="Stream time(minutes)", y="Followers gained", color="Channel", trendline="ols", title="Stream time vs. Followers Gained")
plotly(fig)

# Bar chart of average viewers by language
# which launguage is the most popular??
language_viewers = df.groupby("Language")["Average viewers"].mean().reset_index()

fig = px.bar(
    language_viewers,
    x="Language",
    y="Average viewers",
    title="Average Viewers by Language",
    color="Average viewers"
)
plotly(fig)

# box plot of peak views over diff languages
filtered_box_plot_df = df[df["Peak viewers"] > 10000]

fig = px.box(filtered_box_plot_df, x="Language", y="Peak viewers", title="Peak Viewers Distribution by Language")
plotly(fig)
text("**Note:** The box plot only includes languages where there are 10k+ peak viewers")