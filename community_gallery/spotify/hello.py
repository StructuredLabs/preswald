from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

text("# Spotify Analysis")

# 1. Load the dataset
connect() 
df = get_df('songs_csv')

# 2. Query the dataset
text("### Filter songs based on popularity > 85:")
sql = "SELECT * FROM songs_csv WHERE popularity > 85"
filtered_df = query(sql, "songs_csv")
table(filtered_df)

# 3. Interactive UI
text("### Scatter plot of Popularity vs Danceability:")
threshold = slider("Year", min_val=1998, max_val=2020, default=1998)
year_filtered_df = df[df['year'] == threshold]

fig = px.scatter(year_filtered_df, x='popularity', y='danceability', labels={'popularity': 'Popularity', 'danceability': 'Danceability'})
fig.update_traces(textposition='top center', marker=dict(size=7))
plotly(fig)

# 4. Create a visualization
text("### Scatter plot of Popularity vs Tempo:")
fig1 = px.scatter(df, x='popularity', y='tempo', labels={'popularity': 'Popularity', 'tempo': 'Tempo'})

fig1.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))
fig1.update_layout(template='plotly_white')

plotly(fig1)
