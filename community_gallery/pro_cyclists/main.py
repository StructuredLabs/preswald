import os
import sys
import pandas as pd
from preswald import text, plotly, connect, get_df, table
from preswald import slider
import plotly.express as px


# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('riders_csv')


# Create a scatter plot
fig = px.scatter(df, x='place', y='point', hover_name='name',
                 title='Place vs. Point',
                 labels={'place': 'Place', 'point': 'Point'})

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# Style the plot
fig.update_layout(template='plotly_white')

# Show the plot
plotly(fig)

# Show the data
min_place = slider("Minimum place", min_val=1, max_val=100, default=1)
table(df[df["place"] >= min_place], title="Riders info")

