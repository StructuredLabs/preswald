from preswald import text, table, plotly, connect, get_df, slider
import pandas as pd
import plotly.express as px

# Welcome Message
text("# Spotify Streams Analysis App 🎵")
text("Analyze the most streamed songs on Spotify in 2024.")

# Initialize connection to preswald.toml data sources
connect()


df = get_df("Most_Streamed_Spotify_Songs_2024")


if df is None:
    text("Error: Dataset could not be loaded. Check the dataset name and path.")
else:
    text("Dataset loaded successfully!")

    
    df["Spotify Streams"] = df["Spotify Streams"].str.replace(",", "", regex=True).apply(pd.to_numeric, errors="coerce")
    df["YouTube Views"] = df["YouTube Views"].str.replace(",", "", regex=True).apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=["Spotify Streams", "YouTube Views"])

    # Display Key Metrics
    total_streams = df["Spotify Streams"].sum()
    total_tracks = len(df)
    top_track = df.loc[df["Spotify Streams"].idxmax()]["Track"]
    top_artist = df.loc[df["Spotify Streams"].idxmax()]["Artist"]

    text("""
    ### Key Metrics 📊
    - Total Streams: {:,.0f}
    - Total Tracks: {}
    - Top Track: {} by {}
    """.format(total_streams, total_tracks, top_track, top_artist))

    # Add User Controls: Stream Threshold Slider
    threshold = slider("Stream Threshold", min_val=0, max_val=2500000000, default=500000000)

    # Filter Data Based on User Input
    filtered_df = df[df["Spotify Streams"] > threshold]

    # Display Filtered Data in a Table
    table(filtered_df, title="Top Streamed Songs (Filtered)")

    # Top Artists by Streams (Bar Chart)
    top_artists = filtered_df.groupby("Artist")["Spotify Streams"].sum().nlargest(10).reset_index()
    fig_bar = px.bar(
        top_artists,
        x="Artist",
        y="Spotify Streams",
        title="Top Artists by Spotify Streams",
        labels={"Spotify Streams": "Total Streams"},
        color="Spotify Streams",
        color_continuous_scale="Viridis"
    )
    fig_bar.update_layout(template="plotly_white")
    plotly(fig_bar)

    # Scatter Plot: Spotify Streams vs YouTube Views
    fig_scatter = px.scatter(
        filtered_df,
        x="Spotify Streams",
        y="YouTube Views",
        color="Artist",
        hover_name="Track",
        title="Spotify Streams vs YouTube Views by Artist",
        labels={"Spotify Streams": "Total Spotify Streams", "YouTube Views": "YouTube Views"},
    )
    fig_scatter.update_traces(marker=dict(size=10, opacity=0.8))
    fig_scatter.update_layout(template="plotly_white")
    plotly(fig_scatter)