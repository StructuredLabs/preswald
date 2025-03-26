from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px

text("# Grammy Winners Analysis")
text("A simple analysis of the 67th Grammy Awards (2024)")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('grammy_winners')

# Display basic info
text("## Grammy Awards Dataset")
text(f"Total entries: {len(df)}")

# Filter to only show winners
winners_df = df[df['winner'] == True]
text(f"Number of winners: {len(winners_df)}")

# Create a simple table of winners
table(winners_df[['category', 'artist', 'song_or_album']], title="Grammy Winners 2024")

# Count winners by category
category_counts = winners_df['category'].value_counts().reset_index()
category_counts.columns = ['category', 'count']

# Create a bar chart of winners by category
fig = px.bar(category_counts, x='category', y='count',
             title='Number of Winners by Category',
             labels={'category': 'Award Category', 'count': 'Number of Winners'})

# Improve readability
fig.update_layout(
    xaxis_tickangle=-45,
    height=600,
    template='plotly_white'
)

# Show the plot
plotly(fig)
