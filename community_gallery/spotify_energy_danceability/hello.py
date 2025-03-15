from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

# Load the CSV
connect()
df = get_df('spotify_data')

# Filter Dataset
sql = "SELECT * FROM spotify_data WHERE popularity > 50"
filtered_df = query(sql, "spotify_data")

# Build the UI
text("# Analyzing Popular Spotify Songs for Energy and Danceability")
text("Toggle the below slider to limit the records by popularity.")
threshold = slider("Popularity", min_val=50, max_val=100, default=75)
table(df[df["track_popularity"] > threshold], title="Dynamic Popularity View")

# Create a Scatter Plot for Energy
fig = px.scatter(df[df["track_popularity"] > threshold], x='energy', y='danceability', text='track_name', color="playlist_genre",
                 title='Energy vs. Danceability',
                 labels={'energy': 'Energy', 'danceability': 'Danceability'})

# Adjust Labels
fig.update_traces(mode='markers', hovertemplate='Energy: %{x}<br>Danceability: %{y}')

# Style the Plot
fig.update_layout(template='plotly_white')

# Show the Plot
plotly(fig)

# Explain the Plot
text("From this, we see energy and danceability are somewhat linearly related, indicating they may have something in common. Depending on how the data was calculated, they may be reliant on a third variable: BPM.")