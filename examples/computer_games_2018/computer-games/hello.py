from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px


# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('computer_games_csv')
filtered_by_date = df[pd.to_datetime(df['Date Released'], errors='coerce') > '2018-01-01']
num_games = len(filtered_by_date)
text(f"# All {num_games} Games After 2018")

# Bar Plot of Games by Developer
fig = px.bar(data_frame=filtered_by_date, 
    x="Developer", 
    color="Operating System", 
    hover_data=["Name", "Date Released", "Genre"], 
    title = 'Games By Developer'
)
plotly(fig)

#Scatter Plot of Games by Genre
fig2 = px.scatter(
    filtered_by_date,
    x="Genre",
    color="Operating System",
    title="Games by Genre",
    hover_data=["Name", "Date Released", "Genre"]
)
plotly(fig2)

# Bar Plot of Games by Operating System
fig3 = px.bar(
    filtered_by_date,
    x="Operating System",
    # y="Developer",
    color="Operating System",
    hover_data=["Name", "Date Released", "Genre"],
    title="Games by Operating System"
)
plotly(fig3)

text('## Full List of Games')
table(filtered_by_date)

