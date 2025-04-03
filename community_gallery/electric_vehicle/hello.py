import pandas as pd
import plotly.express as px
from preswald import text, plotly, connect, get_df, table, query, slider

text("# Electric Vehicle Dashboard")
text("## This dashboard provides insights into electric vehicles by model year, manufacturer, and other key attributes.")

# Load the CSV
connect()
df = get_df('sample_csv')

# SQL Query to filter data
sql = "SELECT VIN, County, City, State, `Postal Code`, `Model Year`, Make, Model, `Electric Vehicle Type`, `Electric Range`, `Base MSRP` FROM ev_data WHERE `Model Year` >= 2015 ORDER BY `Electric Range` DESC LIMIT 100"
filtered_df = query(sql, "sample_csv")

# Slider for interactive filtering
threshold = slider("Model Year Threshold", min_val=2010, max_val=2025, default=2015)
table(df[df["Model Year"] >= threshold], title="Dynamic Data View")

# Restrict the data to show only the top 50 rows based on Electric Range
top_df = df.nlargest(50, 'Electric Range')

# Create a scatter plot with enhanced appearance
fig = px.scatter(top_df, x='Model Year', y='Electric Range', text='Model',
                 title='Model Year vs. Electric Range (Top 50)',
                 labels={'Model Year': 'Model Year', 'Electric Range': 'Electric Range'},
                 color='Make', 
                 template='plotly_white')  

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=10, opacity=0.8), textfont=dict(color='black'))

# Style the plot
fig.update_layout(
    title_font=dict(size=24, family='Arial, sans-serif', color='black'),
    xaxis=dict(title_font=dict(size=18, family='Arial, sans-serif', color='black'), tickfont=dict(color='black'), showline=True, linecolor='black'),
    yaxis=dict(title_font=dict(size=18, family='Arial, sans-serif', color='black'), tickfont=dict(color='black'), showline=True, linecolor='black'),
    plot_bgcolor='rgba(255,255,255,1)',  # White background
    paper_bgcolor='rgba(255,255,255,1)',  # White background
)

# Show the plot
plotly(fig)

text("### Thank you for using the Electric Vehicle Dashboard!")