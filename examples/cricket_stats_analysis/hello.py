from preswald import text, plotly, connect, get_df, table, slider, selectbox
import plotly.express as px

text("# Cricket Match Analytics Dashboard")

# Load the CSV
connect()
df = get_df('matches')

# Get unique seasons for dropdown
available_seasons = sorted(df["season"].unique(), reverse=True)
selected_season = selectbox(
    "Select Season",
    options=[str(year) for year in available_seasons],
    default=str(max(available_seasons))
)

# Convert selected season to integer
selected_season = int(selected_season)

# Filter dataset based on selected season
filtered_df = df[df["season"] == selected_season]

# Display the filtered matches
table(filtered_df, title=f" Matches in {selected_season}")

# Chart 1: Winning Margins (Runs vs Wickets)
fig = px.strip(
    filtered_df,
    y="winner",
    x="win_by_runs",
    title=f" Swarm Plot of Winning Margins in {selected_season}",
    labels={"winner": "Winning Team", "win_by_runs": "Runs"},
    color="winner"
)
plotly(fig)

# Chart 2: Win Ratio by Team
win_counts = filtered_df["winner"].value_counts().reset_index()
win_counts.columns = ["Team", "Wins"]

fig2 = px.pie(
    win_counts,
    names="Team",
    values="Wins",
    title=f"Win Ratio by Team in {selected_season}",
    color="Team"
)
plotly(fig2)

# Chart 3: Top 10 Players with Most Player of the Match Awards
top_players = filtered_df["player_of_match"].value_counts().head(10).reset_index()
top_players.columns = ["Player", "Awards"]

fig3 = px.bar(
    top_players,
    x="Awards",
    y="Player",
    orientation="h",
    title=f" Top 10 Players (Player of the Match Awards) in {selected_season}",
    text_auto=True,
    color="Awards"
)
plotly(fig3)

# Chart 4: Most Successful Venues
venue_city_mapping = {
    "Wankhede Stadium": ("Mumbai", 19.0760, 72.8777),
    "M. Chinnaswamy Stadium": ("Bangalore", 12.9716, 77.5946),
    "Eden Gardens": ("Kolkata", 22.5726, 88.3639),
    "Feroz Shah Kotla Ground": ("Delhi", 28.6139, 77.2090),
    "MA Chidambaram Stadium, Chepauk": ("Chennai", 13.0827, 80.2707),
    "Rajiv Gandhi International Stadium, Uppal": ("Hyderabad", 17.3850, 78.4867),
    "Punjab Cricket Association IS Bindra Stadium, Mohali": ("Mohali", 30.7046, 76.7179),
    "Sawai Mansingh Stadium": ("Jaipur", 26.9124, 75.7873),
    "Dr DY Patil Sports Academy": ("Navi Mumbai", 19.0330, 73.0297),
    "Holkar Cricket Stadium": ("Indore", 22.7196, 75.8577),
    "Saurashtra Cricket Association Stadium": ("Rajkot", 22.3039, 70.8022),
    "Green Park": ("Kanpur", 26.4499, 80.3319),
    "Himachal Pradesh Cricket Association Stadium": ("Dharamsala", 32.2190, 76.3234),
    "Shaheed Veer Narayan Singh International Stadium": ("Raipur", 21.2514, 81.6296)
}
venue_wins = filtered_df["venue"].value_counts().head(10).reset_index()
venue_wins.columns = ["Venue", "Matches"]
venue_wins["City"] = venue_wins["Venue"].map(lambda x: venue_city_mapping[x][0] if x in venue_city_mapping else None)
venue_wins["Latitude"] = venue_wins["Venue"].map(lambda x: venue_city_mapping[x][1] if x in venue_city_mapping else None)
venue_wins["Longitude"] = venue_wins["Venue"].map(lambda x: venue_city_mapping[x][2] if x in venue_city_mapping else None)


fig4 = px.scatter_geo(
    venue_wins,
    lat="Latitude",
    lon="Longitude",
    size="Matches",
    hover_name="Venue",
    title=f" Most Successful Venues in {selected_season}",
    projection="natural earth",
    scope="asia"
)
plotly(fig4)
