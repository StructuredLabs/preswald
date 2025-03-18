from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import plotly.express as px

text("# My Data Analysis App")
text("This is my Pokedesk. 🎉")

# Load the CSV
connect()  # load in all sources, which by default is the sample_csv
df = get_df('pokedex_csv')

threshold = slider("Threshold", min_val=0, max_val=255, default=50)
# Create a scatter plot
filtered_df = df[df["hp"] > threshold]
fig = px.scatter(filtered_df, x='name', y='hp', text='id',
                 title='Pokemons',
                 labels={'hp': 'Healthy Points'}
                 )

# fig = df.plot(x='name', y ="hp" kind="line", tittle= "Pokemons")
# Add labels for each point
fig.update_traces(textposition='top center',
                  marker=dict(size=12, color='lightblue'))

# Style the plot
fig.update_layout(template='plotly_white')

# Show the plot
threshold = slider("Threshold", min_val=0, max_val=255, default=50)
plotly(fig)
# Add user controls

# threshold = slider("Threshold", min_val=0, max_val=255, default=50)
table(df[df["hp"] > threshold], title="Dynamic Data View")
# Show the data
# table(df,limit = 20, title = "Pokemons Names")
