from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')

# Create a scatter plot
fig = px.scatter(df, x='Annual Income ($)', y='Spending Score (1-100)', text='CustomerID',
                 title='Annual Income vs Spending Score',
                 labels={'Annual Income ($)': 'Annual Income', 'Spending Score (1-100)': 'Spending Score'})

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# Style the plot
fig.update_layout(template='plotly_white')

# Show the plot
plotly(fig)

# Show the data
table(df)
