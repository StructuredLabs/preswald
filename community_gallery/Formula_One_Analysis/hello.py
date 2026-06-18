from preswald import text, connect, get_df, table, slider, selectbox, query, alert, checkbox
import pandas as pd
from preswald import plotly
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app designed for an F1 Dashboard 🏎️")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('full_results_with_names')
filtered_df = df[(df['year'] == 2024) & (df['driver_name'] == 'Lewis Hamilton')] 

# Create a scatter plot
text(f"# Driver Performance: Starting Grid vs. Final Position (Lewis Hamilton - 2024)")
fig = px.scatter(
    filtered_df,
    x='grid',                
    y='positionOrder',       
    text='driver_name',      
    title='Grid Position vs Final Race Position',
    labels={'grid': 'Starting Grid Position', 'positionOrder': 'Final Race Position'}
)

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# Style the plot
fig.update_layout(template='plotly_white')

# Show the plot
plotly(fig)

# Show the data
#table(df)

### Eg 1: Fastest Lab Speed filtered by year

text(f"# Fastest Lap Speed Filter by Year")
year_list = sorted(df['year'].dropna().unique().tolist())
year_selected = selectbox("Year List", options=year_list)
#year_selected = slider("Select Year", min_val=2015, max_val=2024, default=2015)
speed_threshold = slider("Minimum Fastest Lap Speed (km/h)", min_val=180, max_val=250, default=200)
df['fastestLapSpeed'] = pd.to_numeric(df['fastestLapSpeed'], errors='coerce')
filtered_df = df[(df['year'] == year_selected) & (df['fastestLapSpeed'] > speed_threshold)]
display_df = filtered_df[['driver_name', 'constructor_name', 'fastestLapSpeed', 'name']] 
display_df = display_df.sort_values(by='fastestLapSpeed', ascending=False)
table(display_df, title=f"Drivers with Fastest Lap Speed > {speed_threshold} km/h in {year_selected}")


### Eg 2: Max Points achieved by {driver_names} over the years

text(f"# Max Points achieved by a driver over the years")
driver_list = df['driver_name'].dropna().unique().tolist() 
driver_names = selectbox("Choose Driver to Analyze", options=driver_list)
driver_df = df[df['driver_name'] == driver_names]
driver_points_by_year = driver_df.groupby('year', as_index=False)['points'].max().sort_values('year')
fig = px.bar(
    driver_points_by_year,
    x='year',
    y='points',
    title=f"Max Points per Race for {driver_names} Over the Years",
    labels={'points': 'Max Points', 'year': 'Year'}
)

# Display plot
plotly(fig)

### Eg 3: Constructor wins over the years

text("# Constructor Wins")
year_1 = slider("Start Year", min_val=1950, max_val=2024, default=2010)
year_2 = slider("End Year", min_val=1950, max_val=2024, default=2010)
winners_df = df[
    (df['year'] >= year_1) & 
    (df['year'] <= year_2) & 
    (df['positionOrder'] == 1)
]
constructor_wins = winners_df.groupby('constructor_name', as_index=False).size().rename(columns={'size': 'wins'}).sort_values(by='wins', ascending=False)

fig = px.pie(
    constructor_wins,
    names='constructor_name',
    values='wins',
    title=f"Constructor Wins Distribution ({year_1} - {year_2})",
    hole=0.3  
)

# Display plot
plotly(fig)


### Eg 4: Race wins of a Driver over the years (using query instead of pandas)

text(f"# Race wins of a Driver over the years")
d_list = df['driver_name'].dropna().unique().tolist() 
dn = selectbox("Driver List", options=d_list)
sql = f"""
SELECT 
    year, 
    driver_name, 
    COUNT(*) AS wins
FROM 
    full_results_with_names
WHERE 
    positionOrder = 1 
    AND driver_name = '{dn}'
GROUP BY 
    year, driver_name
ORDER BY 
    year
"""
driver_wins_yearly = query(sql, "full_results_with_names")
selected_driver_wins = driver_wins_yearly[driver_wins_yearly['driver_name'] == dn]
fig = px.line(
    selected_driver_wins,
    x='year',
    y='wins',
    title=f'Race Wins Over the Years: {dn}',
    markers=True,
    labels={'wins': 'Number of Wins', 'year': 'Year'}
)
plotly(fig)


### Eg 5: Most Successful Driver based of Maximum points over the years 1950-2024

text("# Top 15 Most Successful Drivers (by Total Points) over the years 1950-2024")
driver_points = df.groupby('driver_name', as_index=False)['points'].sum().sort_values(by='points', ascending=False) # Sum points for each driver

fig = px.bar(
    driver_points.head(15),
    x='driver_name',
    y='points',
    orientation='v',
    labels={'points': 'Total Career Points', 'driver_name': 'Driver'},
    text='points'
)

fig.update_traces(textposition='outside')

fig.update_layout(yaxis={'categoryorder':'total ascending'})  # High to low
plotly(fig)

## More fun stuff

text("**Fun Stuff**")
alert("Everyone is a Ferrari fan. Even if they say they’re not. They are Ferrari fans.")
checkbox("More to explore and add...")
