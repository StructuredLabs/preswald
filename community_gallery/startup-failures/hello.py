from preswald import text, plotly, connect, get_df, table
import plotly.express as px
from preswald import query
from preswald import slider

text("# Startup failures")
text("Preswald won't ever be in this dataset 🎉")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('startup_failures')

sql = "SELECT * FROM startup_failures WHERE start > 2015"
filtered_df = query(sql, "startup_failures")

# Create a scatter plot
fig = px.scatter(filtered_df, x='start', y='end', text='start',
                 title='Start Date vs. End Date',
                 labels={'start': 'Start', 'end': 'End'})

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

fig.update_layout(
    template='plotly_white'
)

# Show the plot
plotly(fig)

threshold = slider("End year", min_val=2015, max_val=2024, default=2016, step=1)

# Show the data
# table(df)
table(filtered_df[filtered_df["end"] > threshold], title="Dynamic Data View")

