from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('megaGymDataset_csv')

sql = "SELECT * FROM megaGymDataset_csv WHERE Rating > 5.0;"
filtered_df = query(sql, "megaGymDataset_csv")

text("# Data View filtered by Rating")
threshold = slider("Threshold", min_val=0, max_val=10, default=5)
table(df[df['Rating'] > threshold], title="Dynamic Data View")

text("# Quick Overview of Data")
table(df.describe())

text("# Average Rating of Workouts by Equipment")
fig = px.scatter(df.groupby('Equipment')['Rating'].mean().sort_values(ascending=False), y='Rating')
plotly(fig)

text("# Bar Graph of Types of Workouts and their Counts")
fig2 = px.bar(df['Type'].value_counts().reset_index(), x='Type', y='count')
plotly(fig2)

text("# Bar Graph of Difficulty of Workouts and their Counts")
fig3 = px.bar(df['Level'].value_counts().reset_index(), x='Level', y='count')
plotly(fig3)

text("# Average Rating of Workouts by Type")
fig4 = px.scatter(df.groupby('Type')['Rating'].mean().sort_values(ascending=False), y='Rating')
plotly(fig4)