from preswald import text, plotly, connect, get_df, table, text, plotly, slider, selectbox
import pandas as pd
import plotly.express as px

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
seattle_data = get_df('sample_csv')

seattle_data['date'] = pd.to_datetime(seattle_data['date'])  # Convert 'date' to datetime format

# User Interactions
selected_weather = selectbox("Select Weather Type", options=seattle_data['weather'].unique(), default="rain")
min_wind_speed = slider("Minimum Wind Speed", min_val=0, max_val=seattle_data['wind'].max(), default=0)

# Data Filtering
filtered_data = seattle_data[(seattle_data['weather'] == selected_weather) & (seattle_data['wind'] >= min_wind_speed)]

# Displaying Data and Visualizations
text("## Filtered Weather Data and Visualizations")

# Temperature Box Plot
if not filtered_data.empty:
    fig_box = px.box(filtered_data, y=['temp_max', 'temp_min'], title="Temperature Variations")
    plotly(fig_box)
else:
    text("No data available for temperature box plots.")

# Heatmap of Temperature Over Time
if not seattle_data.empty:
    seattle_data['month'] = seattle_data['date'].dt.month  # Extract month for grouping in the heatmap
    fig_heatmap = px.density_heatmap(seattle_data, x='month', y='temp_max', marginal_x="histogram", marginal_y="histogram", title="Monthly Max Temperature Heatmap")
    plotly(fig_heatmap)
else:
    text("No data available for temperature heatmap.")

# Wind Speed vs. Precipitation Scatter Plot
if not filtered_data.empty:
    fig_scatter_wind_precip = px.scatter(filtered_data, x='wind', y='precipitation', color='weather',
                                         title="Wind Speed vs. Precipitation")
    plotly(fig_scatter_wind_precip)
else:
    text("No data available for wind speed vs. precipitation scatter plot.")

# Weather Type Distribution Bar Chart (repeated for continuity)
weather_counts = seattle_data['weather'].value_counts()
fig_weather_types = px.bar(x=weather_counts.index, y=weather_counts.values, labels={'x': 'Weather Type', 'y': 'Count'}, title="Weather Type Frequency")
plotly(fig_weather_types)