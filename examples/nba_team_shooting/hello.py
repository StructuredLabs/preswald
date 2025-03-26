from preswald import text, plotly, connect, get_df, table, selectbox
import plotly.graph_objects as go


# Introduction
text("# NBA Shot Analysis")
text("Analyze shooting patterns from NBA shot location data")

# Connect to data source
connect()  # Configure your CSV in preswald.toml
shots_df = get_df('team_shooting_csv')

# Data preparation
shots_df['MISSED_SHOT'] = 1 - shots_df['SHOT_MADE_FLAG']  # 1 for missed, 0 for made

# Player selection
all_players = shots_df['PLAYER_NAME'].unique().tolist()
selected_player = selectbox("Select a player to analyze:", options=all_players)

# Team selection
all_teams = shots_df['TEAM_NAME'].unique().tolist()
selected_team = selectbox("Select a team to analyze:", options=all_teams)

# # Filter options
filter_option = selectbox("Filter by:", options=["Player", "Team", "All Data"], default="Player")

# Apply filters
if filter_option == "Player":
    filtered_df = shots_df[shots_df['PLAYER_NAME'] == selected_player]
    analysis_title = f"{selected_player}'s Shooting Analysis"
elif filter_option == "Team":
    filtered_df = shots_df[shots_df['TEAM_NAME'] == selected_team]
    analysis_title = f"{selected_team} Team Shooting Analysis"
else:
    filtered_df = shots_df
    analysis_title = "Both Team Shooting Analysis"

# Basic stats
text(f"## {analysis_title}")
text(f"Total shots: {len(filtered_df)}")
text(f"Shots made: {filtered_df['SHOT_MADE_FLAG'].sum()} ({filtered_df['SHOT_MADE_FLAG'].mean()*100:.1f}%)")

# Shot zone breakdown
zone_stats = filtered_df.groupby('SHOT_ZONE_BASIC').agg({
    'SHOT_ATTEMPTED_FLAG': 'sum',
    'SHOT_MADE_FLAG': 'sum'
}).reset_index()
zone_stats['SHOOTING_PCT'] = (zone_stats['SHOT_MADE_FLAG'] / zone_stats['SHOT_ATTEMPTED_FLAG'] * 100).round(2)
zone_stats = zone_stats.sort_values('SHOT_ATTEMPTED_FLAG', ascending=False)

text("## Shot Zone Breakdown")
table(zone_stats)

# Shot type breakdown
type_stats = filtered_df.groupby('SHOT_TYPE').agg({
    'SHOT_ATTEMPTED_FLAG': 'sum',
    'SHOT_MADE_FLAG': 'sum'
}).reset_index()
type_stats['SHOOTING_PCT'] = (type_stats['SHOT_MADE_FLAG'] / type_stats['SHOT_ATTEMPTED_FLAG'] * 100).round(2)

text("## Shot Type Breakdown")
table(type_stats)

# Shot chart visualization
text("## Shot Chart")
fig = go.Figure()

# Add made shots
made_shots = filtered_df[filtered_df['SHOT_MADE_FLAG'] == 1]
fig.add_trace(go.Scatter(
    x=made_shots['LOC_X'], 
    y=made_shots['LOC_Y'],
    mode='markers',
    marker=dict(
        size=8,
        color='green',
        symbol='circle',
        opacity=0.7
    ),
    name='Made Shots'
))

# Add missed shots
missed_shots = filtered_df[filtered_df['SHOT_MADE_FLAG'] == 0]
fig.add_trace(go.Scatter(
    x=missed_shots['LOC_X'], 
    y=missed_shots['LOC_Y'],
    mode='markers',
    marker=dict(
        size=8,
        color='red',
        symbol='x',
        opacity=0.7
    ),
    name='Missed Shots'
))

# Baseline
fig.add_shape(
    type="line", line=dict(color="black", width=2),
    x0=-250, x1=250, y0=0, y1=0
)
# Three-point line 
fig.add_shape(
    type="path",
    path="M -220 0 C -220 140, -80 240, 0 240 C 80 240, 220 140, 220 0",
    line=dict(color="black", width=2)
)
# Free throw line
fig.add_shape(
    type="line", line=dict(color="black", width=2),
    x0=-80, x1=80, y0=190, y1=190
)

fig.update_layout(
    title="Shot Chart",
    xaxis=dict(range=[-300, 300], showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(range=[-50, 400], showgrid=False, zeroline=False, showticklabels=False),
    height=600,
    width=600,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)

plotly(fig)
