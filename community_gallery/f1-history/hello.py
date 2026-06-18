from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

text("# F1 Dataset Analysis")
text("An interactive exploration of Formula 1 racing data throughout history 🏎️")

connect()
winners_df = get_df('winners')
teams_df = get_df('teams_updated')
fastest_laps_df = get_df('fastest_laps_updated')
drivers_df = get_df('drivers_updated')

winners_df['Year'] = pd.to_datetime(winners_df['Date'], errors='coerce').dt.year

text("## 🏆 Top Winning Drivers")
text("Explore the most successful F1 drivers in history based on the number of race wins.")

num_top_drivers = slider("Select number of top drivers to display", min_val=5, max_val=30, default=15)

driver_wins = winners_df['Winner'].value_counts().reset_index()
driver_wins.columns = ['Driver', 'Wins']
driver_wins = driver_wins.sort_values('Wins', ascending=False).head(num_top_drivers)

fig1 = px.bar(
    driver_wins, 
    x='Driver', 
    y='Wins',
    color='Wins',
    color_continuous_scale='Viridis',
    title=f'Top {num_top_drivers} F1 Drivers by Number of Grand Prix Wins',
    labels={'Driver': 'Driver Name', 'Wins': 'Number of Wins'}
)
fig1.update_layout(
    xaxis_tickangle=-45,
    coloraxis_showscale=False,
    hoverlabel=dict(bgcolor="white", font_size=12),
    margin=dict(l=20, r=20, t=40, b=70)
)
plotly(fig1)

text("## 🏎️ Team Performance Trends")
text("Analyze how different teams have performed across F1 seasons.")

min_year_team = slider("Select minimum year for Team Performance", min_val=1950, max_val=2024, default=1950)
max_year_team = slider("Select maximum year for Team Performance", min_val=1950, max_val=2024, default=2024)
teams_filtered = teams_df[(teams_df['year'] >= min_year_team) & (teams_df['year'] <= max_year_team)]

team_year_pivot = teams_filtered.pivot_table(
    index='year', 
    columns='Team', 
    values='PTS', 
    aggfunc='sum'
).fillna(0)

top_teams = teams_filtered.groupby('Team')['PTS'].sum().nlargest(10).index.tolist()
team_year_pivot = team_year_pivot[top_teams]

fig2 = go.Figure()
for team in top_teams:
    fig2.add_trace(go.Scatter(
        x=team_year_pivot.index,
        y=team_year_pivot[team],
        mode='lines',
        stackgroup='one',
        name=team,
        hoverinfo='x+y+name',
        line=dict(width=0.5)
    ))
fig2.update_layout(
    title=f'Points Distribution Among Top 10 Teams from {min_year_team} to {max_year_team}',
    xaxis_title='Year',
    yaxis_title='Points',
    hovermode='x unified',
    legend_title='Team',
    margin=dict(l=20, r=20, t=40, b=20)
)
plotly(fig2)

text("## ⏱️ Fastest Lap Times Evolution")
text("See how lap times have improved over the years in Formula 1, focusing on the iconic Monaco Grand Prix.")

min_year_monaco = slider("Select minimum year for Monaco Lap Times", min_val=1950, max_val=2024, default=1950)
max_year_monaco = slider("Select maximum year for Monaco Lap Times", min_val=1950, max_val=2024, default=2024)
monaco_laps = fastest_laps_df[
    (fastest_laps_df['Grand Prix'] == 'Monaco') & 
    (fastest_laps_df['year'] >= min_year_monaco) & 
    (fastest_laps_df['year'] <= max_year_monaco)
].copy()
monaco_laps = monaco_laps.dropna(subset=['Time', 'year'])

def convert_to_seconds(time_str):
    if pd.isna(time_str) or time_str == '':
        return np.nan
    try:
        if ':' in str(time_str):
            parts = str(time_str).split(':')
            if len(parts) == 2:
                minutes, seconds = parts
                return float(minutes) * 60 + float(seconds)
            elif len(parts) == 3:
                hours, minutes, seconds = parts
                return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        return float(time_str)
    except:
        return np.nan

monaco_laps['TimeInSeconds'] = monaco_laps['Time'].apply(convert_to_seconds)
monaco_laps = monaco_laps.dropna(subset=['TimeInSeconds'])

fig3 = px.scatter(
    monaco_laps, 
    x='year', 
    y='TimeInSeconds', 
    color='Car',
    title=f'Monaco Grand Prix Fastest Lap Times ({min_year_monaco}-{max_year_monaco})',
    labels={'year': 'Year', 'TimeInSeconds': 'Lap Time (seconds)', 'Car': 'Car'},
    hover_data=['Driver', 'Time']
)

if not monaco_laps.empty:
    valid_data = monaco_laps.dropna(subset=['year', 'TimeInSeconds'])
    if len(valid_data) > 1:
        x_values = valid_data['year'].values
        y_values = valid_data['TimeInSeconds'].values
        coeffs = np.polyfit(x_values, y_values, 1)
        polynomial = np.poly1d(coeffs)
        x_range = np.linspace(min(x_values), max(x_values), 100)
        fig3.add_trace(go.Scatter(
            x=x_range,
            y=polynomial(x_range),
            mode='lines',
            name='Trend',
            line=dict(color='red', dash='dash'),
            showlegend=True
        ))
fig3.update_traces(
    marker=dict(size=10, opacity=0.7, line=dict(width=1, color='DarkSlateGrey')),
    selector=dict(mode='markers')
)
fig3.update_layout(
    xaxis_title='Year',
    yaxis_title='Lap Time (seconds)',
    hovermode='closest',
    legend_title='Car Manufacturer',
    margin=dict(l=20, r=20, t=40, b=20)
)
plotly(fig3)

text("## 🌍 Driver Championships by Nationality")
text("Explore which nations have produced the most successful F1 drivers.")

top_n_nationalities = slider("Select number of top nationalities to display", min_val=5, max_val=20, default=10)
nationality_points = drivers_df.groupby(['Nationality', 'year'])['PTS'].sum().reset_index()
top_nationalities = nationality_points.groupby('Nationality')['PTS'].sum().nlargest(top_n_nationalities).index.tolist()
filtered_data = nationality_points[nationality_points['Nationality'].isin(top_nationalities)]
fig4 = px.bar(
    filtered_data,
    x='PTS',
    y='Nationality',
    color='year',
    orientation='h',
    title=f'Championship Points by Nationality and Year (Top {top_n_nationalities} Nations)',
    labels={'PTS': 'Total Points', 'year': 'Year', 'Nationality': 'Country'},
    color_continuous_scale='Viridis',
    height=700
)
fig4.update_layout(
    yaxis={'categoryorder':'total ascending'},
    xaxis_title='Championship Points',
    legend_title='Year',
    margin=dict(l=20, r=20, t=40, b=20),
    bargap=0.15
)
plotly(fig4)

text("## 🗺️ Global Distribution of F1 Drivers")
text("See where Formula 1 drivers come from around the world.")

driver_countries = drivers_df['Nationality'].value_counts().reset_index()
driver_countries.columns = ['Country', 'Number of Drivers']

country_codes = {
    'GBR': 'United Kingdom', 'USA': 'United States', 'ITA': 'Italy', 
    'FRA': 'France', 'GER': 'Germany', 'BRA': 'Brazil', 
    'ARG': 'Argentina', 'AUS': 'Australia', 'BEL': 'Belgium',
    'CAN': 'Canada', 'SUI': 'Switzerland', 'AUT': 'Austria',
    'ESP': 'Spain', 'FIN': 'Finland', 'SWE': 'Sweden',
    'NZL': 'New Zealand', 'MEX': 'Mexico', 'JPN': 'Japan',
    'POR': 'Portugal', 'RUS': 'Russia', 'POL': 'Poland'
}
driver_countries['Country'] = driver_countries['Country'].map(
    {k[:3]: v for k, v in country_codes.items()}
).fillna(driver_countries['Country'])

fig5 = px.choropleth(
    driver_countries,
    locations='Country',
    locationmode='country names',
    color='Number of Drivers',
    hover_name='Country',
    color_continuous_scale='Viridis',
    title='Geographic Distribution of F1 Drivers',
    labels={'Number of Drivers': 'Driver Count'}
)
fig5.update_layout(
    geo=dict(
        showframe=True,
        showcoastlines=True,
        projection_type='natural earth'
    ),
    margin=dict(l=0, r=0, t=40, b=0)
)
plotly(fig5)

text("## ⏱️ Decade-wise Average Lap Times at Monaco")
text("Compare how average lap times at the Monaco Grand Prix have evolved over the decades.")

monaco_laps['Decade'] = (monaco_laps['year'] // 10) * 10
avg_lap_by_decade = monaco_laps.groupby('Decade')['TimeInSeconds'].mean().reset_index()
fig6 = px.line(
    avg_lap_by_decade, 
    x='Decade', 
    y='TimeInSeconds',
    markers=True,
    title='Average Lap Times at Monaco by Decade',
    labels={'Decade': 'Decade', 'TimeInSeconds': 'Average Lap Time (seconds)'}
)
fig6.update_traces(mode='lines+markers')
plotly(fig6)

text("## 🗓️ Races Per Year")
text("Explore how the number of Grand Prix races has evolved over time.")

min_year_races = slider("Select minimum year for Races Per Year", min_val=1950, max_val=2024, default=1950)
max_year_races = slider("Select maximum year for Races Per Year", min_val=1950, max_val=2024, default=2024)
races_per_year = winners_df[(winners_df['Year'] >= min_year_races) & (winners_df['Year'] <= max_year_races)]
races_per_year = races_per_year.groupby('Year').size().reset_index(name='Race Count')
fig7 = px.bar(
    races_per_year,
    x='Year',
    y='Race Count',
    title=f'Number of Races Per Year ({min_year_races}-{max_year_races})',
    labels={'Year': 'Year', 'Race Count': 'Number of Races'}
)
fig7.update_layout(xaxis_tickangle=-45)
plotly(fig7)

text("## Complete F1 Data Tables")
text("Browse the raw data for deeper analysis.")
table(winners_df.head(10))
