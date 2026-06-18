from preswald import text, connect, get_df, table, plotly, slider, query, selectbox as select
import pandas as pd
import plotly.express as px

connect()

races_df = get_df("races_csv")
results_df = get_df("results_csv")
circuits_df = get_df("circuits_csv")
lap_times_df = get_df("lap_times_csv")

races_last_10 = query("SELECT * FROM races_csv WHERE year BETWEEN 2015 AND 2024", "races_csv")

active_drivers_query = query(
    f"SELECT DISTINCT driverId FROM results_csv WHERE raceId IN ({','.join(map(str, races_last_10['raceId'].tolist()))})",
    "results_csv"
)
active_drivers = active_drivers_query['driverId'].tolist()
drivers_df = query(f"SELECT * FROM drivers_csv WHERE driverId IN ({','.join(map(str, active_drivers))})", "drivers_csv")

text("# Formula 1 Hub")

top_circuits = (races_last_10.groupby('circuitId')
                .size()
                .reset_index(name='race_count')
                .merge(circuits_df[['circuitId', 'name']], on='circuitId')
                .sort_values('race_count', ascending=False)
                .head(15))

# Active slider control
circuit_index = slider("Select Circuit Index", min_val=0, max_val=len(top_circuits) - 1, default=0)
circuit_id = top_circuits.iloc[circuit_index]['circuitId']
selected_circuit = top_circuits.iloc[circuit_index]['name']

# Commented selectbox control (dropdown) as an alternative
# circuit_options = top_circuits['name'].tolist()
# selected_circuit = select("Select Circuit", options=circuit_options, default=circuit_options[0])
# circuit_id = top_circuits[top_circuits['name'] == selected_circuit]['circuitId'].iloc[0]

circuit_races = query(f"SELECT * FROM races_csv WHERE circuitId = {circuit_id} AND year BETWEEN 2015 AND 2024",
                      "races_csv")
race_ids = circuit_races['raceId'].tolist()

wins_data = query(
    f"SELECT * FROM results_csv WHERE raceId IN ({','.join(map(str, race_ids))}) AND positionOrder = 1",
    "results_csv"
)
wins_data = wins_data.merge(drivers_df[['driverId', 'forename', 'surname']], on='driverId', how='left')
wins_data['driver_name'] = wins_data['forename'] + ' ' + wins_data['surname']
wins_count = (wins_data.groupby('driver_name')
              .size()
              .reset_index(name='wins')
              .sort_values('wins', ascending=False))

lap_times = query(f"SELECT * FROM lap_times_csv WHERE raceId IN ({','.join(map(str, race_ids))})", "lap_times_csv")
lap_times = lap_times.merge(drivers_df[['driverId', 'forename', 'surname']], on='driverId', how='left')
lap_times['driver_name'] = lap_times['forename'] + ' ' + lap_times['surname']
avg_lap_times = (lap_times.groupby('driver_name')['milliseconds']
                 .mean()
                 .reset_index(name='avg_lap_time'))
avg_lap_times['avg_lap_time_s'] = avg_lap_times['avg_lap_time'] / 1000
avg_lap_times['avg_lap_time_str'] = (avg_lap_times['avg_lap_time_s']
                                     .apply(lambda x: f"{int(x // 60)}:{x % 60:06.3f}"))

chart_layout = dict(
    template='plotly_white',
    font=dict(family="Arial", size=12, color="#333"),
    title_font=dict(size=16, color="#333"),
    margin=dict(l=60, r=60, t=60, b=60),
    height=450,
    paper_bgcolor='rgba(245,245,245,1)',
    plot_bgcolor='rgba(255,255,255,1)'
)

# Wins table with renamed column
wins_table = wins_count[['driver_name', 'wins']].rename(columns={
    'driver_name': 'Driver Name',
    'wins': 'Wins'
})
table(wins_table, title=f"Winners at {selected_circuit} (2015-2024)")

fig_wins = px.bar(wins_count,
                  y='driver_name',
                  x='wins',
                  orientation='h',
                  text=wins_count['wins'].astype(str),
                  color='wins',
                  color_continuous_scale='Blues')
fig_wins.update_traces(textposition='inside', textfont=dict(size=14, color='white'))
fig_wins.update_layout(
    **chart_layout,
    xaxis_title="Number of Wins",
    yaxis_title="Drivers",
    yaxis={'autorange': 'reversed'},
    coloraxis_showscale=False
)
plotly(fig_wins)

top_laps = avg_lap_times.sort_values('avg_lap_time_str').head(10)
top_laps_table = top_laps[['driver_name', 'avg_lap_time_str']].rename(columns={
    'driver_name': 'Driver Name',
    'avg_lap_time_str': 'Avg Lap Time'
})
table(top_laps_table, title="Top 10 Lap Times")

fig_laps = px.scatter(top_laps,
                      x='driver_name',
                      y='avg_lap_time_s',
                      text=top_laps['avg_lap_time_str'],
                      size='avg_lap_time_s',
                      color='avg_lap_time_s',
                      color_continuous_scale='OrRd')
fig_laps.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='DarkSlateGrey')))
fig_laps.update_layout(
    **chart_layout,
    xaxis_title="Drivers",
    yaxis_title="Average Lap Time",
    yaxis=dict(
        range=[top_laps['avg_lap_time_s'].min() * 0.98, top_laps['avg_lap_time_s'].max() * 1.02],
        tickmode='linear',
        tick0=int(top_laps['avg_lap_time_s'].min()),
        dtick=1
    ),
    xaxis_tickangle=-45,
    coloraxis_showscale=False
)
plotly(fig_laps)
