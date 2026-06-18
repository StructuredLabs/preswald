from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px
from preswald import query, slider
import plotly.graph_objects as go
import json


text("# Welcome to Preswald!")
text("NBA season 2023-24 Stats analysis 🏀")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('nba_season_2023_24_csv')

sql = f"""
SELECT 
    game_id
    , start_time
    , period
    , home_id
    , home_name
    , home_score
    , home_rebounds
    , home_assists
    , home_fg_pct
    , home_3p_pct
    , home_ft_pct
    , home_record
    , home_linescores
    , away_id
    , away_name
    , away_score
    , away_rebounds
    , away_assists
    , away_fg_pct
    , away_3p_pct
    , away_ft_pct
    , away_record
    , away_linescores
    , venue_name
    , venue_city
    , venue_state
    , broadcasts
FROM nba_season_2023_24_csv
"""
filtered_df = query(sql, "nba_season_2023_24_csv")
# table(filtered_df)

text("Select month and year from below slider to view stats.")
month_threshold = slider("Month", min_val=1, max_val=12, default=10)
year_threshold = slider("Year", min_val=2023, max_val=2024, default=2023)

datewise_sql = f"""
SELECT * from nba_season_2023_24_csv
where partition_month = {month_threshold} and partition_year = {year_threshold}
-- limit 5
"""
datewise_query = query(datewise_sql, "nba_season_2023_24_csv")
table(datewise_query, title="Dynamic Data View")

fig = px.line_polar(
    df,
    r=[df['HOME_FG_PCT'].mean(), df['HOME_3P_PCT'].mean(), df['HOME_FT_PCT'].mean()],
    theta=['FG%', '3P%', 'FT%'],
    line_close=True,
    title="Home Team Shooting Efficiency"
)

venue_counts = df['VENUE_NAME'].value_counts().head(10).reset_index()
venue_counts.columns = ['VENUE_NAME', 'GAME_COUNT']

fig = px.bar(
    venue_counts,
    x='VENUE_NAME',
    y='GAME_COUNT',
    title="Top 10 Venues by Number of Games Hosted"
)
fig.update_xaxes(categoryorder='total descending')
plotly(fig)

df['START_TIME'] = pd.to_datetime(df['START_TIME'])
df['YEAR_MONTH'] = df['START_TIME'].dt.to_period('M').astype(str)

# Group by month and calculate average scores
score_trend = df.groupby('YEAR_MONTH').agg({'HOME_SCORE':'mean', 'AWAY_SCORE':'mean'}).reset_index()

fig = px.line(
    score_trend,
    x='YEAR_MONTH',
    y=['HOME_SCORE', 'AWAY_SCORE'],
    title="Average Home vs. Away Scores Over Time",
    labels={'value': 'Average Score', 'variable': 'Team Type'}
)
plotly(fig)

fig = go.Figure()
fig.add_trace(go.Box(y=df['HOME_SCORE'], name='Home Scores'))
fig.add_trace(go.Box(y=df['AWAY_SCORE'], name='Away Scores'))
fig.update_layout(title="Distribution of Home vs. Away Scores")
plotly(fig)


df['HOME_POINTS_LEADER'] = df['HOME_LEADERS'].apply(
    lambda x: json.loads(x).get('points', {}).get('name', 'Unknown')
)

# Count top scorers
top_scorers = df['HOME_POINTS_LEADER'].value_counts().head(10).reset_index()
top_scorers.columns = ['PLAYER', 'COUNT']

fig = px.bar(
    top_scorers,
    x='PLAYER',
    y='COUNT',
    title="Top 10 Home Team Points Leaders"
)
plotly(fig)
