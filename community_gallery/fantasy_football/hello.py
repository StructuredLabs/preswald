from preswald import text, plotly, connect, get_df, table, selectbox, text_input, query
import plotly.express as px

text("# Fantasy Football Analysis")
text("Discover insights from players' performance data 🏈")

# Load the CSV
connect() # load in all sources
cleaned_merged_seasons = get_df('cleaned_merged_seasons')

cleaned_merged_seasons = cleaned_merged_seasons[cleaned_merged_seasons['minutes'] > 0].copy()
# Filter out players with zero minutes
cleaned_merged_seasons = cleaned_merged_seasons[cleaned_merged_seasons['minutes'] > 0].copy()

# Add interactive filter components
text("## Filter Options")
text("Use these controls to explore different aspects of the data")

# Position filter
position_options = ["All Positions"] + sorted(cleaned_merged_seasons["position"].unique().tolist())
selected_position = selectbox("Select Position:", position_options)

# Season filter if multiple seasons exist
if "season_x" in cleaned_merged_seasons.columns:
    season_options = ["All Seasons"] + sorted(cleaned_merged_seasons["season_x"].unique().tolist())
    selected_season = selectbox("Select Season:", season_options)

# Data Limit
data_limit = 10
data_limit = text_input("Enter the number of rows to display:")
try:
    data_limit = int(data_limit)
except ValueError:  
    data_limit = 10

# Show the data based on filters
text("## Filtered Data")
text("Showing data based on your filters:")

sql_query = 'SELECT * FROM cleaned_merged_seasons' + ' WHERE minutes > 0' + " AND position LIKE '%" + selected_position + "%'"
str(selected_season)
filtered_data = query(sql_query, "cleaned_merged_seasons")

# Display the filtered data
table(data=filtered_data, limit=data_limit)

text("## Player Value vs. Fantasy Points")
text("Are expensive players worth the investment?")

fig1 = px.scatter(
    cleaned_merged_seasons,
    x='value',
    y='total_points',
    color='position',
    hover_name='name',
    title='Fantasy Points vs Player Value',
    labels={
        'value': 'Player Value (£0.1M)',
        'total_points': 'Fantasy Points',
        'position': 'Position'
    },
    opacity=0.7
)


fig1.update_layout(template='plotly_white')
plotly(fig1)

text("## Fantasy Points by Position")
text("How do different positions compare in fantasy point production?")

fig2 = px.box(
    cleaned_merged_seasons,
    x='position',
    y='total_points',
    color='position',
    title='Distribution of Fantasy Points by Position',
    labels={
        'position': 'Position',
        'total_points': 'Fantasy Points'
    }
)

fig2.update_layout(template='plotly_white')
plotly(fig2)
