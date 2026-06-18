from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px
from preswald import query, slider

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('males_data')

sql = "SELECT * FROM males_data WHERE Year < 2020"
filtered_df = query(sql, "males_data")

# Create a scatter plot
fig = px.scatter(filtered_df, x='United States', y='Year', text='Year',
                 title='United States vs. Year',
                 labels={'united States': 'United States', 'year': 'Value'})

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# Style the plot
fig.update_layout(template='plotly_white')

# Show the plot
plotly(fig)

# Show the data
text("# My Data Analysis App")
threshold = slider("Threshold", min_val=1991, max_val=2019, default=2015)
table(filtered_df[filtered_df["Year"] > threshold], title= 'Dynamic Data View')

fig = px.scatter(filtered_df[filtered_df["Year"] > threshold], x="India", y="Year", color="India")
plotly(fig)