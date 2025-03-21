import pandas as pd
import plotly.express as px

from preswald import connect, get_df, plotly, table, text


text("# ⚽ English Premier League Football Analysis")
text("Analysis of Premier League matches")

# Load the CSV
connect()  # load in all sources
df = get_df("sample_csv")

# Create a scatter plot of shots vs goals
fig = px.scatter(
    df,
    x="H Shots",
    y="FTH Goals",
    title="Shot Conversion Analysis",
    labels={"H Shots": "Home Team Shots", "FTH Goals": "Home Team Goals"},
    color="League",
    hover_data=["HomeTeam", "AwayTeam", "Date"],
)

# Add styling
fig.update_traces(marker=dict(size=10, opacity=0.7), selector=dict(mode="markers"))

# Style the plot
fig.update_layout(template="plotly_white", hovermode="closest")

# Show the plot
plotly(fig)

# Calculate total goals by team for pie chart
text("## ⚽ Goals Distribution")
text("Total goals scored by each team in the Premier League")

premier_league_df = df[df["League"] == "Premier League"]
team_goals = (
    pd.concat(
        [
            premier_league_df.groupby("HomeTeam")["FTH Goals"].sum(),
            premier_league_df.groupby("AwayTeam")["FTA Goals"].sum(),
        ]
    )
    .groupby(level=0)
    .sum()
    .sort_values(ascending=False)
)


pie_fig = px.pie(
    values=team_goals.values,
    names=team_goals.index,
    title="Distribution of Goals Scored by Team",
    hole=0.3,  # Makes it a donut chart
    color_discrete_sequence=px.colors.qualitative.Set3,
)

pie_fig.update_traces(textposition="inside", textinfo="percent+label")
pie_fig.update_layout(showlegend=False, template="plotly_white")

plotly(pie_fig)

# Calculate league table
text("## 🏆 League Standings")
text("Current Premier League table based on match results")


def calculate_points(group):
    wins = (group["FT Result"] == "H").sum() * 3
    draws = (group["FT Result"] == "D").sum()
    return wins + draws


# Calculate home points
home_points = (
    premier_league_df.groupby("HomeTeam").apply(calculate_points).reset_index()
)
home_points.columns = ["Team", "Home_Points"]

# Calculate away points (need to adjust for away wins)
away_df = premier_league_df.copy()
away_df["FT Result"] = away_df["FT Result"].map({"A": "H", "H": "A", "D": "D"})
away_points = away_df.groupby("AwayTeam").apply(calculate_points).reset_index()
away_points.columns = ["Team", "Away_Points"]

# Combine points
league_table = pd.merge(home_points, away_points, on="Team", how="outer").fillna(0)
league_table["Total_Points"] = league_table["Home_Points"] + league_table["Away_Points"]
league_table = league_table.sort_values("Total_Points", ascending=False)


bar_fig = px.bar(
    league_table.head(10),
    x="Team",
    y="Total_Points",
    title="Top 10 Teams by Points",
    labels={"Total_Points": "Points", "Team": "Club"},
    color="Total_Points",
    color_continuous_scale="Viridis",
)

bar_fig.update_layout(template="plotly_white", xaxis_tickangle=-45)

plotly(bar_fig)

# Show detailed statistics
text("## 📊 Team Performance")
league_table["Rank"] = range(1, len(league_table) + 1)
league_table = league_table[
    ["Rank", "Team", "Total_Points", "Home_Points", "Away_Points"]
]
table(league_table)
