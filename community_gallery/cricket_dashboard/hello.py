from preswald import text, plotly, connect, get_df, table, slider
import plotly.express as px

text("# Welcome to the Cricket Runs Dashboard! 🏏")
text("Visualizing the top cricket statistics from IPL 2022.")

# Connect and load the dataset
connect()
df = get_df('sample_csv')


min_runs = slider("Select Minimum Runs", min_val=int(df['Runs'].min()), max_val=int(df['Runs'].max()), default=200)
df_filtered = df[df['Runs'] >= min_runs]

# Top 10 Run Scorers Bar Chart
fig1 = px.bar(df_filtered.nlargest(10, 'Runs'), x='Player', y='Runs',
              title='Top 10 Run Scorers in 2022',
              labels={'Runs': 'Total Runs', 'Player': 'Player'},
              color='Runs',
              color_continuous_scale='blues')
plotly(fig1)

# Strike Rate Distribution for Top 5 Players in the data
top_players = df.nlargest(5, 'Runs')
fig2 = px.histogram(top_players, x='SR', nbins=20,
                    title='Strike Rate Distribution for Top 5 Players',
                    labels={'SR': 'Strike Rate'},
                    color='Player',
                     color_discrete_sequence=['#FFB6C1', '#87CEFA', '#98FB98', '#FFDAB9', '#E6E6FA'])
plotly(fig2)

# Runs vs Balls Faced Heatmap with Player Labels for filtered data
fig3 = px.density_heatmap(df_filtered, x='BF', y='Runs', z='Runs',
                          title='Runs vs. Balls Faced (Heatmap)',
                          labels={'BF': 'Balls Faced', 'Runs': 'Total Runs'},
                          color_continuous_scale='blues',
                          hover_data={'Player': True})
plotly(fig3)

text("# Top 50 players with score of 200 plus in IPL 2022🏏")
table(df_filtered)