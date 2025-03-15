from preswald import connect, get_df, table, text, slider, plotly
import plotly.express as px

connect()


df = get_df("players")

if df is None:
    text("### Error: Dataset could not be loaded. Please check the file path and format.")
else:
    text(f"### Debug: Dataset Loaded with {len(df)} rows")


    text("# Football Players Analysis App")


    table(df, title="Complete Player Dataset")


    rating_threshold = slider("Minimum Overall Age", min_val=0, max_val=200, default=80)


    filtered_df = df[df["Age"] >= rating_threshold]


    if filtered_df.empty:
        text("### No players meet the selected criteria.")
    else:
        table(filtered_df, title="Filtered Players")


        fig = px.scatter(filtered_df, x="Name", y="Value", color="Club", title="Player Value vs. Overall Rating")
        plotly(fig)
