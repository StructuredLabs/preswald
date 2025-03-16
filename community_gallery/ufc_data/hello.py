from preswald import connect, text, table, slider, plotly, get_df, query
import plotly.express as px
import pandas as pd

# Step 1: Set up the dashboard header
text("# UFC Fighter Stats Dashboard")
connect()  # Initialize connection to preswald.toml data sources

# Step 2: Get the data
# Try to get the dataframe, with error handling
try:
    df = get_df('UFC_Records_csv')
    text("✅ Data loaded successfully!")
except Exception as e:
    text(f"⚠️ Error loading data: {str(e)}")
    text("Using sample data instead...")
    df = pd.read_csv('data/UFC_Records.csv', columns=['Type of Record', 'Rank', 'Name', 'Total'])

try:
    sql = "SELECT * FROM UFC_Records_csv WHERE Name = 'Charles Oliveira'"
    charles_df = query(sql, "UFC_Records_csv")
    oliveira_df = charles_df[charles_df['Name'] == 'Charles Oliveira']
    columns_to_display = ["Type of Record", "Name", "Total"]
    filtered_columns_df = oliveira_df[columns_to_display]
    text("## Charles Oliveira Accomplishments")
    table(filtered_columns_df, title="Charles Oliveira's Records")
except Exception as e:
    text(f"⚠️ Error displaying finishes data: {str(e)}")

min_fights = slider("Minimum Number of Fights", min_val=30, max_val=45, default=35)

try:
    filtered_df = df[(df['Type of Record'] == 'Total Fights') & (df['Total'] >= min_fights)]
    
    text(f"## Fighters with {min_fights}+ UFC Fights")
    table(filtered_df, title="Fighter Fight Count")
    
    if not filtered_df.empty:
        fig = px.bar(
            filtered_df,
            x='Name',
            y='Total',
            color='Total',
            title=f"UFC Fighters with {min_fights}+ Fights",
            labels={'Total': 'Number of Fights', 'Name': 'Fighter'},
            color_continuous_scale='blues'
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        plotly(fig)
    else:
        text(f"No fighters found with {min_fights} or more fights.")
except Exception as e:
    text(f"⚠️ Error filtering data: {str(e)}")