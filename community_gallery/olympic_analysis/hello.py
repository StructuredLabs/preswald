from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

text("# 🏅 Olympic Games Analysis")
text("Analyzing medal distributions in Olympic Games")

# Load the CSV
connect()
df = get_df('olympics')

# Add interactive controls
min_year = int(df['Year'].min())
max_year = int(df['Year'].max())
year_threshold = slider("Select Year", min_val=min_year, max_val=max_year, default=2020)

# Query data using SQL
sql_query = f"SELECT * FROM olympics WHERE Year >= {year_threshold} ORDER BY Total DESC"
filtered_df = query(sql_query, "olympics")

# Create visualization
fig = px.scatter(
    filtered_df, 
    x='Gold', 
    y='Total', 
    text='NOC',
    color='Year',
    title=f'Gold vs Total Medals (Year >= {year_threshold})',
    labels={
        'Gold': 'Gold Medals', 
        'Total': 'Total Medals',
        'Year': 'Olympic Year'
    },
    color_continuous_scale='Viridis'
)

# Add labels for each point
fig.update_traces(textposition='top center')

# Style the plot
fig.update_layout(template='plotly_white')

# Show the plot
plotly(fig)

# Show filtered data view
text("## 🏆 Medal Table")
text(f"Showing data for years {year_threshold} onwards")
table(filtered_df[['Year', 'NOC', 'Gold', 'Silver', 'Bronze', 'Total']])