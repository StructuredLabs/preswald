from preswald import connect, get_df, table, text, slider, plotly
import plotly.express as px

text("# ⚽ FC 24 Player Stats Explorer")

connect()
df = get_df("all_fc_24_players").head(1000)

table(df.head(10), title="📋 Sample Player Data")
threshold = slider("🎚️ Minimum Overall Rating", min_val=50, max_val=99, default=85)
filtered_df = df[df["overall"] >= threshold]
table(filtered_df.head(20), title=f"⭐ Top {len(filtered_df)} Players (showing first 20)")
fig = px.scatter(
    filtered_df,
    x="age",
    y="overall",
    color="position",
    hover_data=["name", "club", "nation"],
    title="📈 Overall Rating vs Age by Position"
)
plotly(fig)
