from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px

connect()

df = get_df("highdiamond")
sql = "SELECT * FROM highdiamond WHERE blueWardsPlaced > 50"
filtered_df = query(sql, "highdiamond")

text("# High Diamond Ranked 10min Data Analysis")

table(filtered_df, title="Filtered Data (blueWardsPlaced > 50)")

text("## Dynamic Filtering with Sliders")

# filter the DataFrame using both sliders
kill_threshold = slider("Minimum Blue Kills", min_val=0, max_val=30, default=10)
ward_threshold = slider("Minimum Blue Wards Placed", min_val=0, max_val=200, default=50)
slider_filtered_df = df[
    (df["blueKills"] >= kill_threshold) &
    (df["blueWardsPlaced"] >= ward_threshold)
    ]

table(slider_filtered_df, title="Games Passing Both Thresholds")

text("## Distribution of Blue Kills")
fig_hist = px.histogram(
    df,
    x="blueKills",
    nbins=20,
    title="Histogram of Blue Kills"
)
plotly(fig_hist)

text("## Box Plot of Blue Total Gold by Win/Loss")
fig_box = px.box(
    df,
    y="blueTotalGold",
    color="blueWins",
    title="Blue Team Total Gold by Outcome"
)
plotly(fig_box)

text("## Correlation Heatmap")
numeric_cols = [
    "blueKills",
    "blueDeaths",
    "blueWardsPlaced",
    "blueTotalGold",
    "redKills",
    "redWardsPlaced",
    "redTotalGold"
]
corr_df = df[numeric_cols].corr()
fig_heatmap = px.imshow(
    corr_df,
    text_auto=True,
    title="Correlation Matrix",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1
)
plotly(fig_heatmap)

text("## Aggregated Stats by Outcome")
sql_agg = """
SELECT 
    blueWins, 
    AVG(blueWardsPlaced) AS avgWards, 
    AVG(blueKills) AS avgKills,
    AVG(blueTotalGold) AS avgGold
FROM highdiamond
GROUP BY blueWins
"""
aggregated_df = query(sql_agg, "highdiamond")
table(aggregated_df, title="Average Wards, Kills, and Gold by Win/Loss")

text("## Quick Stats")
games_count = len(df)
blue_wins = df["blueWins"].sum()
win_rate = (blue_wins / games_count) * 100

text(f"- **Total Games**: {games_count}")
text(f"- **Blue Side Wins**: {blue_wins}")
text(f"- **Blue Side Win Rate**: {win_rate:.2f}%")
