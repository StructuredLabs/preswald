# Import necessary libraries
from preswald import text, plotly, connect, get_df, slider, selectbox
import pandas as pd
import plotly.express as px

text("# Spotify 2023 Streaming Analysis\n\n"
     "Analyzing Spotify's Streaming Landscape: Insights into Popular Artists, Hit Songs, and Industry Trends.\n\n"
    "**Author:** Sailesh Dwivedy  \n"
     "**Email:** sailesh.dwivedy@colorado.edu  \n"
     "**University:** University of Colorado Boulder  \n"
     "**Data:** [Most Streamed Spotify Songs 2023](https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023/data)")

# Load dataset
connect()
df = get_df("spotify_2023")  # Ensure dataset key matches

# Fix column names
df.columns = df.columns.str.strip()

# Convert necessary columns to appropriate data types
df["streams"] = pd.to_numeric(df["streams"], errors="coerce").astype(float)
df["released_year"] = pd.to_numeric(df["released_year"], errors="coerce").astype(int)
df["bpm"] = pd.to_numeric(df["bpm"], errors="coerce").astype(float)

# Convert streams to billions
df["streams_billion"] = df["streams"] / 1e9

# ------------------------------
# Add Sliders & Select Box for Interactive Filtering
# ------------------------------
cumulative = df['released_year'].value_counts(normalize=True).sort_index(ascending=False).cumsum()
year_95 = cumulative[cumulative > 0.95].index[0] # Taking 95% threshold record contribution as min year
min_year = int(year_95)
max_year = int(df["released_year"].max())
selected_year = slider("Filter by Release Year", min_val=min_year, max_val=max_year, default=min_year)

# Set up slider for streams in billions
max_streams_billion = df["streams_billion"].max()
stream_threshold = slider("Minimum Streams (Billions)", min_val=0.0, max_val=max_streams_billion, default=max_streams_billion * 0.1)

min_bpm = float(df["bpm"].min())
max_bpm = float(df["bpm"].max())
selected_bpm = slider("Filter by BPM (Tempo)", min_val=min_bpm, max_val=max_bpm, default=min_bpm)

# Add a select box to choose filtering mode
filter_mode = selectbox("Choose Year Filter Mode", ["All Time", "Only Selected Year", "From Selected Year Onward"])

# Apply Filters Based on Selection
if filter_mode == "Only Selected Year":
    filtered_df = df[
        (df["streams_billion"] >= stream_threshold) &
        (df["released_year"] == selected_year) &  # Exact year match
        (df["bpm"] >= selected_bpm)
    ]
elif filter_mode == "From Selected Year Onward":
    filtered_df = df[
        (df["streams_billion"] >= stream_threshold) &
        (df["released_year"] >= selected_year) &  # Selected year and beyond
        (df["bpm"] >= selected_bpm)
    ]
else:  # "All Time", no year restriction
    filtered_df = df[
        (df["streams_billion"] >= stream_threshold) &
        (df["bpm"] >= selected_bpm)
    ]

# ------------------------------
# Generate Visualizations and Dynamic Insights
# ------------------------------
if filtered_df.empty:
    text("No data available for the selected filters. Try adjusting the sliders.")
else:
    # ------------------------------
    # Top Artists by Total Streams
    # ------------------------------
    text("## 1. Top Artists by Total Streams")
    artist_streams = (
        filtered_df.groupby("artist(s)_name")["streams_billion"]
        .sum()
        .reset_index()  # Ensure artist names are in a proper DataFrame
        .sort_values(by="streams_billion", ascending=False)
        .head(10)
    )

    fig1 = px.bar(
        artist_streams,
        x="artist(s)_name",
        y="streams_billion",
        title=f"Top Artists by Total Streams ({filter_mode})",
        labels={"artist(s)_name": "Artist", "streams_billion": "Total Streams (B)"},
    )

    plotly(fig1)

    # Generate Insights
    top_artist = artist_streams.iloc[0]["artist(s)_name"]
    top_artist_streams = artist_streams.iloc[0]["streams_billion"]
    other_top_artists = artist_streams.iloc[1:5]["artist(s)_name"].tolist()  # Get 2nd to 5th top artists
    other_top_artists_list = ", ".join(other_top_artists)

    text(
        "### Insights from Top Artists:\n"
        f"- **{top_artist} is the most-streamed artist**, with approximately **{top_artist_streams:.2f}B streams**, dominating global streaming charts.\n"
        f"- Other major streaming giants include **{other_top_artists_list}**, each accumulating billions of streams and shaping the global music landscape.\n"
        "- These artists maintain massive influence across multiple genres and platforms, consistently securing top spots in playlists and charts.\n\n"
        "### Conclusion:\n"
        "While the #1 artist holds the crown, the rest of the Top artists are equally influential, each contributing to trends in global music."
    )

    # ------------------------------
    # Most Streamed Songs
    # ------------------------------
    text("## 2. Most Streamed Songs")
    top_songs = filtered_df.nlargest(10, "streams_billion")
    fig2 = px.bar(
        x=top_songs["track_name"],
        y=top_songs["streams_billion"],
        title=f"Most Streamed Songs ({filter_mode})",
        labels={"x": "Song", "y": "Streams (B)"}
    )
    plotly(fig2)

    # Generate Insights
    top_song = top_songs.iloc[0]["track_name"]
    top_song_streams = top_songs.iloc[0]["streams_billion"]
    other_top_songs = top_songs.iloc[1:5]["track_name"].tolist()  # Get 2nd to 5th top songs
    other_top_songs_list = ", ".join(other_top_songs)

    text(
        "### Insights from Most Streamed Songs:\n"
        f"- **'{top_song}' is the most-streamed song**, with **{top_song_streams:.2f}B streams**, making it one of the biggest hits of the year.\n"
        f"- Other massive global hits include **{other_top_songs_list}**, each attracting billions of streams and dominating airwaves worldwide.\n"
        "- These tracks define the cultural soundscape, with viral success on streaming and global charts.\n\n"
        "### Conclusion:\n"
        "While one song may take the top spot, the rest of the Top tracks reflect a mix of viral hits, international chart-toppers, and long-lasting anthems."
    )

    # ------------------------------
    # Streams vs. BPM (Filtered)
    # ------------------------------
    text("## 3. How Does BPM Affect Streaming Popularity?")
    fig3 = px.scatter(filtered_df, x="bpm", y="streams_billion", title=f"Streams vs. BPM ({filter_mode})", labels={"x": "BPM (Tempo)", "y": "Streams (B)"})
    plotly(fig3)

    # Generate Insights
    avg_bpm = filtered_df["bpm"].mean()
    highest_bpm_song = filtered_df.loc[filtered_df["bpm"].idxmax(), "track_name"]
    highest_bpm = filtered_df["bpm"].max()

    text(
        "### Insights from BPM vs Streams:\n"
        f"- **The average BPM for top-streamed songs is {avg_bpm:.0f}**, suggesting most popular songs have a moderate tempo.\n"
        f"- **The fastest song is '{highest_bpm_song}' with a BPM of {highest_bpm}**, likely indicating a high-energy dance track.\n\n"
        "### Conclusion:\n"
        "Most streamed songs fall within a tempo range that appeals to casual and dance listeners alike. High BPM tracks tend to be in dance or electronic genres."
    )

    # ------------------------------
    # Seasonal Trends in Song Releases
    # ------------------------------
    text("## 4. Trends in Song Releases Over the Years")
    monthly_releases = filtered_df.groupby("released_year").size()
    fig4 = px.line(x=monthly_releases.index, y=monthly_releases.values, markers=True, title=f"Songs Released by Year ({filter_mode})", labels={"x": "Year", "y": "Number of Songs"})
    plotly(fig4)

    # Generate Insights
    peak_year = monthly_releases.idxmax()
    peak_releases = monthly_releases.max()
    earliest_year = monthly_releases.idxmin()
    lowest_releases = monthly_releases.min()

    text(
        "### Insights from Release Year Trends:\n"
        f"- **Most songs were released in {peak_year}, with {peak_releases} songs added that year.**\n"
        f"- **The earliest songs in the dataset date back to {earliest_year}, with only {lowest_releases} releases.**\n\n"
        "### Conclusion:\n"
        "Recent years have seen a rise in song releases, possibly due to increased streaming platforms, independent artists, and global collaborations."
    )

# ------------------------------
# Song Characteristics vs. Popularity
# ------------------------------
text("## 5. How Do Song Characteristics Relate to Popularity?")

# Scatter Plot: Energy vs Streams
fig_energy = px.scatter(filtered_df, x="energy_%", y="streams_billion", title="Energy vs. Streams", labels={"x": "Energy (%)", "y": "Streams (B)"})
plotly(fig_energy)

# Scatter Plot: Danceability vs Streams
fig_dance = px.scatter(filtered_df, x="danceability_%", y="streams_billion", title="Danceability vs. Streams", labels={"x": "Danceability (%)", "y": "Streams (B)"})
plotly(fig_dance)

# Box Plot: Happiness (Valence) of Top-Streamed Songs
fig_valence = px.box(filtered_df, x="valence_%", title="Happiness (Valence) of Top-Streamed Songs", labels={"x": "Valence (%)"})
plotly(fig_valence)

# Generate Insights
avg_energy = filtered_df["energy_%"].mean()
avg_danceability = filtered_df["danceability_%"].mean()
avg_valence = filtered_df["valence_%"].mean()

text(
    "### Insights from Song Characteristics:\n"
    f"- **The average energy level of top-streamed songs is {avg_energy:.2f}%**, suggesting that high-energy tracks often attract more listeners.\n"
    f"- **The average danceability score is {avg_danceability:.2f}%**, indicating that danceable songs generally perform well in terms of streams.\n"
    f"- **The average happiness (valence) score is {avg_valence:.2f}%**, meaning that the most popular songs tend to have a mix of happy and melancholic tones.\n\n"
    "### Conclusion:\n"
    "High-energy and danceable songs tend to perform better. While happier songs are popular, a mix of moods also works well."
)

# ------------------------------
# Do Playlist Placements Boost Song Streams?
# ------------------------------
text("## 6. Do Playlist Placements Boost Song Streams?")

# Fix playlist columns & compute total playlist placements
filtered_df["in_spotify_playlists"] = pd.to_numeric(filtered_df["in_spotify_playlists"], errors="coerce").fillna(0)
filtered_df["in_apple_playlists"] = pd.to_numeric(filtered_df["in_apple_playlists"], errors="coerce").fillna(0)
filtered_df["in_deezer_playlists"] = filtered_df["in_deezer_playlists"].str.replace(",", "", regex=True).astype(float)
filtered_df["in_deezer_playlists"] = pd.to_numeric(filtered_df["in_deezer_playlists"], errors="coerce").fillna(0)

# Compute "Total Playlists" inside the filtered dataset
filtered_df["Total Playlists"] = filtered_df[["in_spotify_playlists", "in_apple_playlists", "in_deezer_playlists"]].sum(axis=1)

# Grouped Bar Chart – Playlist Distribution Across Platforms
playlist_counts = filtered_df[["in_spotify_playlists", "in_apple_playlists", "in_deezer_playlists"]].sum()
fig_playlist_bar = px.bar(
    x=playlist_counts.index,
    y=playlist_counts.values,
    title="Songs in Spotify vs. Apple vs. Deezer Playlists",
    labels={"x": "Platform", "y": "Total Playlist Count"}
)
plotly(fig_playlist_bar)

# Scatter Plot – Playlist Count vs Streams
fig_playlist_scatter = px.scatter(
    filtered_df,
    x="Total Playlists",
    y="streams_billion",
    title="Playlist Count vs. Streams",
    labels={"x": "Total Playlist Count", "y": "Streams (B)"}
)
plotly(fig_playlist_scatter)

# Generate Insights
max_playlist_platform = playlist_counts.idxmax()
max_playlists = playlist_counts.max()
avg_playlists = filtered_df["Total Playlists"].mean()

text(
    "### Insights from Playlist Placements:\n"
    f"- **The platform with the most playlist placements is {max_playlist_platform}, with approximately {max_playlists:,.0f} playlist inclusions.**\n"
    f"- **On average, a song appears in {avg_playlists:.0f} playlists across platforms.**\n"
    "- **Songs that appear in more playlists tend to have higher stream counts, proving playlist exposure matters.**\n\n"
    "### Conclusion:\n"
    "Getting a song featured in major playlists significantly increases its visibility and streaming numbers."
)


# ------------------------------
# Seasonal Trends in Song Releases
# ------------------------------
text("## 7. What Are the Seasonal Trends in Song Releases?")

# Bar Chart – Number of Songs Released by Month
monthly_releases = filtered_df.groupby("released_month").size()
fig_monthly_releases = px.bar(
    x=monthly_releases.index,
    y=monthly_releases.values,
    title="Number of Songs Released by Month",
    labels={"x": "Month", "y": "Songs Released"}
)
plotly(fig_monthly_releases)

# Line Chart – Streams Trend by Month
monthly_streams = filtered_df.groupby("released_month")["streams_billion"].sum()
fig_stream_trend = px.line(
    x=monthly_streams.index,
    y=monthly_streams.values,
    markers=True,
    title="Streams Trend by Month",
    labels={"x": "Month", "y": "Total Streams (B)"}
)
plotly(fig_stream_trend)

# Generate Insights
peak_month = monthly_releases.idxmax()
peak_stream_month = monthly_streams.idxmax()

text(
    "### Insights from Seasonal Trends:\n"
    f"- **Most songs are released in month {peak_month}, suggesting a strategic release trend.**\n"
    f"- **The month with the highest total streams is {peak_stream_month}, indicating peak listening trends.**\n\n"
    "### Conclusion:\n"
    "Artists and labels often time song releases based on seasonal demand and industry patterns."
)


# ------------------------------
# Key & Mode Distributions of Popular Songs
# ------------------------------
text("## 8. What Are the Key & Mode Distributions of Popular Songs?")

# Bar Chart – Most Common Musical Keys
key_counts = filtered_df["key"].value_counts()
fig_key_distribution = px.bar(
    x=key_counts.index,
    y=key_counts.values,
    title="Most Common Musical Keys",
    labels={"x": "Musical Key", "y": "Count"}
)
plotly(fig_key_distribution)

# Pie Chart – Major vs Minor Mode Distribution
mode_counts = filtered_df["mode"].value_counts()
fig_mode_distribution = px.pie(
    names=mode_counts.index,
    values=mode_counts.values,
    title="Major vs. Minor Mode Distribution"
)
plotly(fig_mode_distribution)

# Generate Insights
most_common_key = key_counts.idxmax()
most_common_mode = mode_counts.idxmax()

text(
    "### Insights from Key & Mode Distribution:\n"
    f"- **The most commonly used key is {most_common_key}, making it a popular choice for commercial music.**\n"
    f"- **{most_common_mode} mode dominates, showing the industry preference.**\n\n"
    "### Conclusion:\n"
    "Understanding the most successful keys and modes can help artists and producers make data-driven creative choices."
)

