from preswald import text, plotly, connect, get_df, table, slider, checkbox
import plotly.express as px

text("# Gaming Industry Trends Analysis Dashboard")
text("""
Welcome to the interactive dashboard that provides insights into key metrics of the gaming industry.  
Explore how revenue relates to player engagement, track industry trends over time, and analyze market distribution across genres, platforms, and more.
""")

# Load the CSV Data
connect()
df = get_df('gaming_industry_trends')

text("---")

# User Controls
text("## Filter & Explore")
text("Use the controls below to filter the data and discover insights.")

text("### Genre Selection")
text("Select which game genres to include in the analysis:")
genre_options = sorted(df["Genre"].unique().tolist())
select_all = checkbox("Select All Genres", default=True)

genre_selections = {
    genre: checkbox(genre, default=select_all)
    for genre in genre_options
}
text("---")

text("### Release Year Range")
text("Filter games by their release year:")
min_year = int(df["Release Year"].min())
max_year = int(df["Release Year"].max())
year_start = slider("Start Year", min_val=min_year, max_val=max_year, default=min_year)
year_end = slider("End Year", min_val=min_year, max_val=max_year, default=max_year)

text("---")

if select_all:
    df_filtered = df.copy()
else:
    selected_genres = [genre for genre, is_selected in genre_selections.items() if is_selected]
    df_filtered = df[df["Genre"].isin(selected_genres)]

df_filtered = df_filtered[(df_filtered["Release Year"] >= year_start) & (df_filtered["Release Year"] <= year_end)]

text("## 📈 Key Insights")
text("Explore key metrics and trends based on your filter selections.")

# Scatter Plot (Revenue vs. Players)
text("### Revenue vs. Player Base")
text("This chart shows the relationship between game revenue and player count. Bubble size represents peak concurrent players.")
fig_scatter = px.scatter(
    df_filtered,
    x="Revenue (Millions $)",
    y="Players (Millions)",
    size="Peak Concurrent Players",
    color="Genre",
    hover_data=["Game Title", "Developer", "Metacritic Score"],
)
fig_scatter.update_layout(
    margin={'l':20, 'r':20, 't':50, 'b':20},
    xaxis_title="Revenue (Millions $)",
    xaxis={'tickangle': 45},
    yaxis_title="Players (Millions)"
)
plotly(fig_scatter)

text("---")

# Line Chart (Revenue Trends by Genre Over Time)
text("### Revenue Trends by Genre Over Time")
text("Compare how the average revenue for each game genre has evolved over the years.")
df_genre_year = df_filtered.groupby(["Genre", "Release Year"]).agg({
    "Revenue (Millions $)": "mean",
}).reset_index()

fig_line = px.line(
    df_genre_year,
    x="Release Year",
    y="Revenue (Millions $)",
    color="Genre",
    markers=True,
    line_shape="spline"
)
fig_line.update_layout(
    margin={'l':20, 'r':20, 't':50, 'b':20},
    xaxis_title="Release Year",
    xaxis={'tickangle': 45},
    yaxis_title="Avg. Revenue (Millions $)",
    height=600
)
plotly(fig_line)

text("---")

# Bar Graph (Developers by Total Revenue)
text("### Leading Developers")
text("Discover the game studios dominating the market by total revenue generated.")
df_developer = df_filtered.groupby("Developer")["Revenue (Millions $)"].sum().reset_index()
df_developer = df_developer.sort_values(by="Revenue (Millions $)", ascending=False)
fig_bar = px.bar(
    df_developer,
    x="Developer",
    y="Revenue (Millions $)",
    color="Developer",
)
fig_bar.update_layout(
    margin={'l':20, 'r':20, 't':50, 'b':20},
    xaxis={'tickangle': 45},
    xaxis_title="Developer",
    yaxis_title="Total Revenue (Millions $)",
)
plotly(fig_bar)

text("---")

# Pie Chart (Distribution of Games by Platform)
text("### Platform Distribution")
text("How games are distributed across different gaming platforms.")
df_platform = df_filtered["Platform"].value_counts().reset_index()
df_platform.columns = ["Platform", "Count"]
fig_pie = px.pie(
    df_platform,
    names="Platform",
    values="Count",
)
fig_pie.update_layout(
    margin={'l':20, 'r':20, 't':50, 'b':20},
)
plotly(fig_pie)

text("---")

# Full Data Exploration
text("## Detailed Data Explorer")
text("Browse the complete filtered dataset below to see all available metrics and details.")
table(df_filtered)