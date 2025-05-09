import pandas as pd
import plotly.express as px

df = pd.read_csv('data/sample.csv')
fig = px.scatter(df, x='quantity', y='value', text='item',
                 title='Quantity vs. Value',
                 labels={'quantity': 'Quantity', 'value': 'Value'})

fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))
fig.update_layout(template='plotly_white')

# Displays
import preswald

preswald.text("# Welcome to Preswald!")
preswald.text("This is your first app. 🎉")
preswald.plotly(fig)
preswald.table(df)