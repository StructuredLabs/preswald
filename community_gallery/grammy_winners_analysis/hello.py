from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import plotly.express as px

text("# Grammy Winners Analysis - Historical Data")
text("A comprehensive analysis of Grammy Award winners across multiple years")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('grammy_winners')

# Display basic info
text("## Grammy Awards Dataset")
text(f"Total entries: {len(df)}")

# Get the unique years for the filter
years = sorted(df['year'].unique().tolist())
min_year = min(years)
max_year = max(years)

# Create a year filter
text("## Filter by Year")
selected_year = slider("Select Year", min_val=min_year, max_val=max_year, default=max_year)

# Filter data by year
year_filtered_df = df[df['year'] == selected_year]

# Filter to only show winners for the selected year
winners_year_df = year_filtered_df[year_filtered_df['winner'] == True]
text(f"Number of entries for {selected_year}: {len(year_filtered_df)}")
text(f"Number of winners for {selected_year}: {len(winners_year_df)}")

# Create a simple table of winners for the selected year
table(winners_year_df[['category', 'artist', 'song_or_album']], title=f"Grammy Winners for {selected_year}")

# Count winners by category
category_counts = winners_year_df['category'].value_counts().reset_index()
category_counts.columns = ['category', 'count']

# Create a bar chart of winners by category
fig = px.bar(category_counts, x='category', y='count', 
             title=f'Number of Winners by Category for {selected_year}',
             labels={'category': 'Award Category', 'count': 'Number of Winners'})

# Improve readability
fig.update_layout(
    xaxis_tickangle=-45,
    height=600,
    template='plotly_white'
)

# Show the plot
plotly(fig)

# Display all-time winners stats
text("## All-Time Grammy Winners")
all_winners_df = df[df['winner'] == True]
text(f"Total number of winners across all years: {len(all_winners_df)}")

# Create a year-by-year winners chart
winners_by_year = all_winners_df.groupby('year').size().reset_index()
winners_by_year.columns = ['year', 'count']

fig_timeline = px.line(winners_by_year, x='year', y='count',
                       title='Number of Grammy Winners by Year',
                       labels={'year': 'Year', 'count': 'Number of Winners'})
plotly(fig_timeline)
