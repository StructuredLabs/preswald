import pandas as pd
import plotly.express as px
from preswald import plotly, text

text("# Most Streamed Songs in 2024 with Grammy Nominees")
text(
    """
Let's explore 2025 Grammy nominee's music data using most streamed songs
in 2024! Here are the list of some nominees:

**2025 Grammy Nominees**
- Beyonce
- Billie Eilish
- Sabrina Carpenter
- Chappell Roan
- Charli xcx
- Kendrick Lamar
""",
)

# Load data
data = pd.read_csv(
    "./examples/music/data/most_streamed_spotify_songs_2024.csv",
    encoding="unicode_escape",
)

# Extract nominee data
nominee_list = [
    "Beyonce",
    "Billie Eilish",
    "Sabrina Carpenter",
    "Chappell Roan",
    "Charli xcx",
    "Kendrick Lamar",
]
nominee_data = data[data["Artist"].isin(nominee_list)]

# Compare total streams
text("## Total Streams by Each Nominee (Spotify + YouTube + TikTok)")

nominee_data["Total Stream"] = (
    nominee_data["Spotify Streams"]
    + nominee_data["YouTube Views"]
    + nominee_data["TikTok Views"]
)

fig_box = px.box(
    nominee_data,
    x="Artist",
    y="Total Stream",
    title="Total Streams by Nominee",
)
plotly(fig_box)

text(
    """
Beyonce has the most streams out of all 2025 Grammy nominees.
Her highest streaming song reached 12 billion in 2024!
""",
)

# YouTube vs TikTok views correlation
text("## Correlation between Youtube and Tiktok Views")

fig_scatter = px.scatter(
    nominee_data,
    x="YouTube Views",
    y="TikTok Views",
    title="Youtube and Tiktok Views",
    hover_name="Track",
)
plotly(fig_scatter)

# Stream count per album
text("## Total Stream Count Per Album - Top 10 (Spotify + YouTube + TikTok)")
album_data = nominee_data.groupby(["Album Name", "Artist"], as_index=False, sort=True)[
    "Total Stream"
].sum()
album_data = album_data.sort_values("Total Stream", ascending=False)
album_top_ten = album_data.head(10)

fig_bar = px.bar(
    album_top_ten,
    x="Album Name",
    y="Total Stream",
    title="Album Total Stream Count",
    height=600,
    hover_name="Artist",
)
fig_bar.update_layout(
    xaxis_fixedrange=True,
    yaxis_fixedrange=True,
    modebar_remove=[
        "zoom",
        "pan",
        "zoomIn",
        "zoomOut",
        "autoScale",
        "resetScale",
        "orbitRotation",
        "tableRotation",
    ],
)
plotly(fig_bar)

text(
    """
The 2024 Album of The Year is "TEXAS HOLD \'EM" by Beyonce - which surprisingly
placed 3rd in stream count. Though Beyonce still beat the rest with "RENAISSANCE,"
released in 2022!
""",
)
