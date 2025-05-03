from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import plotly.express as px

text("# Welcome to NBA.csv!")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('nba_csv')

from preswald import slider, button

# Two sliders sharing a row
slider1 = slider("Min Age", min_val=df['Age'].min(), max_val=df['Age'].max(), default=df['Age'].min(), size=0.5)
slider2 = slider("Max Age", min_val=df['Age'].min(), max_val=df['Age'].max(), default=df['Age'].max(), size=0.5)

# filter the data
df = df[(df['Age'] >= slider1) & (df['Age'] <= slider2)]

df['Salary'] = pd.to_numeric(df['Salary'], errors='coerce')

numeric_df = df.select_dtypes(include='number')

fig = px.scatter(df, x='Age', y='Salary', color='Team', hover_name='Name',
                 title='Age vs. Salary of NBA Players',
                 labels={'Age': 'Age', 'Salary': 'Salary', 'Name': 'Name', 'Team': 'Team'})

fig2 = px.line(df.groupby('Team')[numeric_df.columns].mean().reset_index(), x='Team', y='Salary', title='Average Salary by Team')


fig.update_layout(template='plotly_white')
fig2.update_layout(template='plotly_white')


# Show the plot
plotly(fig)

plotly(fig2)


# Show the data
table(df)
