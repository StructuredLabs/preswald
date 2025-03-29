import pandas as pd
import plotly.express as px
from preswald import connect, get_df, plotly, text

# Connect to all data sources
connect()

# Data Loading and Preprocessing
def load_and_preprocess_data():
    """Loads and preprocesses the necessary F1 data."""

    # Get dataframes using preswald
    races = get_df("races_csv")
    results = get_df("results_csv")
    drivers = get_df("drivers_csv")
    constructors = get_df("constructors_csv")
    circuits = get_df("circuits_csv")

    # Data preprocessing
    races['year'] = pd.to_numeric(races['year'])
    results['points'] = pd.to_numeric(results['points'], errors='coerce')
    results['position'] = pd.to_numeric(results['position'], errors='coerce')
    results['milliseconds'] = pd.to_numeric(results['milliseconds'], errors='coerce')

    # Merge key datasets
    race_results = pd.merge(results, races, on='raceId')
    race_results = pd.merge(race_results, drivers, on='driverId')
    race_results = pd.merge(race_results, constructors, on='constructorId')

    return race_results, races, drivers, constructors, circuits


def get_driver_standings(race_results, year):
    """Calculates and returns the driver standings for a given year."""
    year_data = race_results[race_results['year'] == year]
    driver_points = year_data.sort_values(['round'])
    driver_points = driver_points.groupby(['driverRef', 'round'])['points'].sum().groupby('driverRef').cumsum().reset_index()
    # driver_points = driver_points.groupby(['driverRef', 'round'])['points'].sum().reset_index()
    # driver_points['points_so_far'] = driver_points.groupby('driverRef')['points'].cumsum()
    return driver_points


def analyze_constructor_wins(race_results, year):
    """Analyzes constructor wins for a given year and returns the results."""
    year_data = race_results[race_results['year'] == year]
    constructor_wins = year_data[year_data['position'] == 1].groupby('constructorRef').size().reset_index(name='wins')
    return constructor_wins


def analyze_circuit_performance(race_results, year, driver):
    """Analyzes circuit performance for a driver in a given year."""
    year_data = race_results[race_results['year'] == year]
    if driver:
        # Filter for the specific driver and create an explicit copy to avoid SettingWithCopyWarning
        driver_circuit = year_data[year_data['driverRef'] == driver].copy()
        
        # Handle DNFs by converting null/NaN position values to 0
        driver_circuit['position'] = driver_circuit['position'].fillna(0)
        
        # Check if 'status' column exists before trying to use it
        if 'status' in driver_circuit.columns:
            # For cases where status indicates DNF but position is not NaN
            dnf_statuses = ['Accident', 'Collision', 'Engine', 'Gearbox', 'Mechanical', 'Retired']
            mask = driver_circuit['status'].str.contains('|'.join(dnf_statuses), case=False, na=False)
            driver_circuit.loc[mask, 'position'] = 0
        
        # Abbreviate "Grand Prix" to "GP" in circuit names
        if 'name_x' in driver_circuit.columns:  # This should be the circuit name
            driver_circuit['name_x'] = driver_circuit['name_x'].str.replace('Grand Prix', 'GP')
        
        return driver_circuit
    else:
        return None

def analyze_driver_performance(race_results, year, driver, metric='points'):
    """Analyzes driver performance against their teammate in a given year for a specific metric."""
    year_data = race_results[race_results['year'] == year]
    if driver:
        driver_data = year_data[year_data['driverRef'] == driver]
        # Find the constructor/team of the driver in the selected year
        constructor_id = driver_data['constructorId'].iloc[0]
        team_data = year_data[year_data['constructorId'] == constructor_id]
        teammate_data = team_data[team_data['driverRef'] != driver]

        # Combine driver and teammate data
        # Make sure to add driver name to data BEFORE concatting
        driver_data['driver'] = driver_data['driverRef']  # Add a 'driver' column
        teammate_data['driver'] = teammate_data['driverRef']  # Add a 'driver' column
        combined_data = pd.concat([driver_data, teammate_data])
        
        # Select only the columns we need to prevent plotly errors:
        combined_data = combined_data[['raceId', 'round', 'driverRef', 'driver', 'laps', 'milliseconds', metric]]

        return combined_data
    else:
        return None
    
def analyze_race_pace(laptimes, race_results, year, driver):
    """Analyzes race pace for a given driver in a given year."""
    year_races = race_results[race_results['year'] == year]['raceId'].unique()

    if driver:
        # Filter lap times for races in the selected year and for the specified driver
        driver_lap_times = laptimes[(laptimes['raceId'].isin(year_races)) & (laptimes['driverId'] == race_results[race_results['driverRef'] == driver]['driverId'].iloc[0])]

        if not driver_lap_times.empty:
            return driver_lap_times
        else:
            print(f"No lap time data available for driver {driver} in year {year}")
            return None
    else:
        return None
    
def analyze_team_driver_points(race_results, selected_year):
    """Analyzes points progression for drivers in each team for a given year."""
    year_data = race_results[race_results['year'] == selected_year]
    
    # Get unique constructors for the selected year
    constructors = year_data['constructorRef'].unique()
    team_driver_charts = {}
    
    for constructor in constructors:
        # Filter data for this constructor
        team_data = year_data[year_data['constructorRef'] == constructor]
        
        # Get drivers for this team
        team_drivers = team_data['driverRef'].unique()
        
        # Calculate cumulative points for each driver in this team
        team_points_data = []
        for driver in team_drivers:
            driver_data = team_data[team_data['driverRef'] == driver].sort_values('round')
            
            # Calculate cumulative points for this driver
            driver_data['cumulative_points'] = driver_data['points'].cumsum()
            
            # Add to team data
            team_points_data.append(driver_data)
        
        # Combine all driver data for this team
        if team_points_data:
            combined_team_data = pd.concat(team_points_data)
            team_driver_charts[constructor] = combined_team_data
    
    return team_driver_charts

def generate_visualization(data, chart_type, x_col, y_col, color_col=None, title=""):
    """Generates a Plotly visualization based on the provided data and parameters."""
    if chart_type == "bar":
        fig = px.bar(data, x=x_col, y=y_col, color=color_col, title=title)
    elif chart_type == "line":
        fig = px.line(data, x=x_col, y=y_col, color=color_col, title=title)
        # Add markers to highlight each data point
        fig.update_traces(mode='lines+markers', marker=dict(size=8))
        # Add grid to make reading values easier
        fig.update_layout(
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                dtick=1  # Show grid line for each round
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            plot_bgcolor='white'  # White background for better grid visibility
        )
    else:
        raise ValueError("Unsupported chart type")
    return fig

# --- Main Analysis Script ---

race_results, races, drivers, constructors, circuits = load_and_preprocess_data()

# Define analysis parameters
selected_year = 2021  # Change this year to analyze different seasons
selected_driver = 'norris' # Driver to analyze

# 1. Analyze Driver Standings
text("## 🏎️ Driver Standings")
driver_standings = get_driver_standings(race_results, selected_year)
driver_standings_fig = generate_visualization(data=driver_standings,
                                              chart_type="line",
                                              x_col="round",
                                              y_col="points",
                                              color_col="driverRef",
                                              title=f"Driver Points Progression - {selected_year}")
plotly(driver_standings_fig)

# 2. Analyze Constructor Wins
text("## 🏆 Constructor Wins")
constructor_wins = analyze_constructor_wins(race_results, selected_year)
constructor_wins_fig = generate_visualization(constructor_wins, "bar", "constructorRef", "wins",
                                            title=f"Constructor Wins in {selected_year}")
plotly(constructor_wins_fig)

# 3. Analyze Circuit Performance for a Specific Driver
text (f"## 🏁 {selected_driver.upper()} Circuit Performance")
circuit_performance = analyze_circuit_performance(race_results, selected_year, selected_driver)
if circuit_performance is not None:
    circuit_viz_data = circuit_performance.copy()
    
    # Convert position to F1 points system (more intuitive)
    def position_to_points(pos):
        if pos == 0:
            return 0
        elif pos <= 10:
            return [25, 18, 15, 12, 10, 8, 6, 4, 2, 1][int(pos) - 1]
        else:
            return 0
    
    # Apply the points conversion
    circuit_viz_data['points_equivalent'] = circuit_viz_data['position'].apply(position_to_points)
    
    # Create a status column for better display
    def get_position_display(pos):
        if pos == 0:
            return "DNF"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(pos if pos < 20 else pos % 10, "th")
            return f"{int(pos)}{suffix}"
    
    circuit_viz_data['position_display'] = circuit_viz_data['position'].apply(get_position_display)
    
    # Sort circuits by performance (better to worse)
    circuit_viz_data = circuit_viz_data.sort_values('points_equivalent', ascending=False)
    
    # Create a figure with subplots for more control
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    # Add lines (stems of the lollipop)
    fig.add_trace(go.Scatter(
        x=circuit_viz_data['name_x'],
        y=circuit_viz_data['points_equivalent'],
        mode='lines',
        line=dict(color='gray', width=1),
        hoverinfo='skip'
    ))
    
    # Define colors based on position categories
    def get_marker_color(pos):
        if pos == 0:  # DNF
            return '#C0392B'  # Red
        elif pos <= 3:  # Podium
            return '#00A020'  # Green
        elif pos <= 10:  # Points
            return '#2E86C1'  # Blue
        else:  # No points
            return '#FFC300'  # Yellow
    
    # Create marker colors list
    marker_colors = [get_marker_color(pos) for pos in circuit_viz_data['position']]
    
    # Add markers (circles of the lollipop)
    fig.add_trace(go.Scatter(
        x=circuit_viz_data['name_x'],
        y=circuit_viz_data['points_equivalent'],
        mode='markers',
        marker=dict(
            size=12,
            color=marker_colors,
            line=dict(width=1, color='black')
        ),
        text=circuit_viz_data['position_display'],
        hovertemplate="<b>%{x}</b><br>Position: %{text}<br>Points: %{y}<extra></extra>"
    ))
    
    # Customize the layout
    fig.update_layout(
        title=f"{selected_driver} Performance by Circuit - {selected_year}",
        xaxis=dict(
            title="Circuits",
            tickangle=90,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title="Points Equivalent",
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickvals=[25, 18, 15, 12, 10, 8, 6, 4, 2, 1, 0],
            ticktext=["1st (25)", "2nd (18)", "3rd (15)", "4th (12)", "5th (10)", 
                      "6th (8)", "7th (6)", "8th (4)", "9th (2)", "10th (1)", "No Points/DNF"]
        ),
        plot_bgcolor='white',
        showlegend=False
    )
    
    # Add a legend for position categories
    legend_items = [
        {"name": "Podium", "color": "#00A020"},
        {"name": "Points", "color": "#2E86C1"},
        {"name": "No Points", "color": "#FFC300"},
        {"name": "DNF", "color": "#C0392B"}
    ]
    
    for i, item in enumerate(legend_items):
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color=item["color"]),
            name=item["name"]
        ))
    
    plotly(fig)
else:
    # create an empty dataframe so it doesn't error
    empty_df = pd.DataFrame({'message': ['No driver selected']})
    plotly(empty_df)
    print("No driver selected or no data available for the selected driver.")

# 5. Analyze Driver Points Progression by Team
text("## 📊 Driver Points Progression by Team")
team_driver_charts = analyze_team_driver_points(race_results, selected_year)

# Generate and display a chart for each team
for team, team_data in team_driver_charts.items():
    if team not in ['red_bull', 'mercedes', 'ferrari']:
        continue
    team_chart = generate_visualization(
        team_data, 
        "line", 
        "round", 
        "cumulative_points", 
        color_col="driverRef",
        title=f"{team} - Driver Points Progression {selected_year}"
    )
    
    # Add customization to the chart
    team_chart.update_layout(
        xaxis_title="Race Round",
        yaxis_title="Cumulative Points",
        legend_title="Drivers",
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        hovermode="closest"
    )
    
    # Enhance hover information to show exact values
    team_chart.update_traces(
        hovertemplate="<b>Round:</b> %{x}<br><b>Points:</b> %{y}<extra></extra>"
    )
    
    plotly(team_chart)