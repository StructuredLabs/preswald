from preswald import text, plotly, connect, get_df, table, slider, selectbox, query
import pandas as pd
import plotly.express as px

text("# California Wildfire Damage\n (2014-2023) 101 incedents recorded")
text("year 2024 on the slider will display all records")
# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('california_csv')
df = df.head(100)

# Create a slider for selecting the number of rows to display
year = slider(
    label="Year to Display",
    min_val=2014,
    max_val=2024,
    step=1,
    default=2017
)

df["Date"] = pd.to_datetime(df["Date"])
filtered_df = df[df["Date"].dt.year == year]

if year == 2024:
  filtered_df = df
  

choice = selectbox(
    label="Choose a column",
    options=["Homes_Destroyed", "Businesses_Destroyed","Estimated_Financial_Loss (Million $)"], 
    default=["Homes_Destroyed"], 
    size=1.0
) 

# Create a scatter plot
fig = px.bar(filtered_df, x='Location', y=choice, color='Cause', text='Incident_ID',
                 title=f"Location vs. {choice}",
                 labels={'Location': 'Location  by county', })


# Add labels for each point
fig.update_traces(textposition='outside')

# Style the plot
fig.update_layout(template='plotly_white')

# Show the plot
plotly(fig)

# Show the data
table(filtered_df)
