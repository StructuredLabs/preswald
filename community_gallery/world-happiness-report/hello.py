from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This plot shows the World Happiness Report 2024 rankings and scores for the happiest countries.")

connect()
df = get_df('hcw')

# Create a scatter plot
fig = px.scatter(df, x='HappiestCountriesWorldHappinessReportRankings2024', y='HappiestCountriesWorldHappinessReportScore2024', text='country',
                 title='Ranking vs Score by Country',
                 labels={'reportRanking': 'Ranking', 'reportScore': 'Score'})

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# Style the plot
fig.update_layout(template='plotly_white')

# Show the plot
plotly(fig)

# Show the data
table(df)
