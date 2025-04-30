import pandas as pd
import plotly.express as px

from preswald import connect, get_df, plotly, table, text, selectbox, slider, button

# Load the CSV
connect()
df = get_df("twitch")

# Taking values and ensuring proper data types
df["Watch time(Minutes)"] = pd.to_numeric(df["Watch time(Minutes)"], errors="coerce")
df["Followers"] = pd.to_numeric(df["Followers"], errors="coerce")
df["Followers gained"] = pd.to_numeric(df["Followers gained"], errors="coerce")
df["Partnered"] = df["Partnered"].map({True: "Yes", False: "No"})
df["Mature"] = df["Mature"].map({True: "Yes", False: "No"})

# UI Header
text("# Twitch Analytics Dashboard")
text("An interactive analysis of Twitch's top streamers, viewership trends, and audience insights.")

# Filters
top_n = slider("Select number of top streamers", min_val=5, max_val=50, default=10)
language_filter = selectbox("Filter by Language", options=["All"] + sorted(df["Language"].unique()), default="All")
partner_filter = selectbox("Partnered Streamers", options=["All", "Yes", "No"], default="All")
mature_filter = selectbox("Mature Content Streamers", options=["All", "Yes", "No"], default="All")

if button("Apply Filters"):
    filtered_df = df.copy()
    if language_filter != "All":
        filtered_df = filtered_df[filtered_df["Language"] == language_filter]
    if partner_filter != "All":
        filtered_df = filtered_df[filtered_df["Partnered"] == partner_filter]
    if mature_filter != "All":
        filtered_df = filtered_df[filtered_df["Mature"] == mature_filter]
    
    # Bar graph: Top Streamers by Watch Time
    top_streamers = filtered_df.nlargest(top_n, "Watch time(Minutes)")
    fig1 = px.bar(
        top_streamers,
        x="Channel",
        y="Watch time(Minutes)",
        title=f"Top {top_n} Streamers by Watch Time",
        text_auto=True,
        color="Followers gained"
    )
    plotly(fig1)
    
    # Pie Chart: Language Distribution
    lang_counts = filtered_df["Language"].value_counts().reset_index()
    lang_counts.columns = ["Language", "Count"]
    fig3 = px.pie(
        lang_counts,
        names="Language",
        values="Count",
        title="Twitch Audience Language Distribution",
        hole=0.4,
    )
    plotly(fig3)

    # Bar graph: Top Streamers by Average Viewers
    top_viewers = filtered_df.nlargest(top_n, "Average viewers")
    fig4 = px.bar(
        top_viewers,
        x="Channel",
        y="Average viewers",
        title=f"Top {top_n} Streamers by Average Viewers",
        text_auto=True,
        color="Followers gained"
    )
    plotly(fig4)
    
    # Display Data Table
    text("## Full Dataset Table")
    table(filtered_df)
