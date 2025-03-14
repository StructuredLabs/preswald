from preswald import text, plotly, connect, get_df, table, query, slider
import plotly.express as px

text("# Pokedex Application")
# text("This is your first app. 🎉")

# Load the CSV
connect()  # Load in all sources, which by default is the sample_csv
df = get_df('pokedex')

# Query or manipulate the data
sql = "SELECT * FROM pokedex WHERE weight > 500"
filtered_df = query(sql, "pokedex")

# Build an interactive UI
text("## Analyzing Pokedex Data")
table(filtered_df, title="Pokemon (Weight > 500)")

# Add a slider for dynamic filtering
text("## Dynamic Filtering")
threshold = slider("Filter Pokemon by HP", min_val=0, max_val=max(df["hp"]), default=50)
table(df[df["hp"] > threshold], title="Pokedex Dynamic View")

# Create a visualization
text("## Visualization (Scatter Plot)")
fig = px.scatter(
    filtered_df, 
    x="attack", 
    y="defense", 
    color="type", 
    title='Attack vs. Defense (Pokemon Weight > 500)', 
    labels={'attack': 'Attack', 'defense': 'Defense'}
)
plotly(fig)

# # Create a scatter plot
# fig = px.scatter(df, x='quantity', y='value', text='item',
#                  title='Quantity vs. Value',
#                  labels={'quantity': 'Quantity', 'value': 'Value'})

# # Add labels for each point
# fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# # Style the plot
# fig.update_layout(template='plotly_white')

# # Show the plot
# plotly(fig)

# # Show the data
# table(df)
