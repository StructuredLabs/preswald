import pandas as pd
from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px

# Connect to Preswald
connect()

df = get_df('project_report_csv')

# Display the first few rows of the dataset
text("## PROJECT MANAGEMENT DASHBOARD 💰💵")
text("Here is the dataset loaded into the application:")

# Show the table
table(df)

# Data Manipulation
# Convert Start_Date and End_Date to datetime
df['Start_Date'] = pd.to_datetime(df['Start_Date'])
df['End_Date'] = pd.to_datetime(df['End_Date'])

# Calculate the duration of each project
df['Duration'] = (df['End_Date'] - df['Start_Date']).dt.days

# Create a slider for filtering by budget
budget_slider = slider("Select Budget Range", min_val=0, max_val=100000, default=50000)

# Query to filter data based on budget
filtered_df = df[df['Budget'] <= budget_slider]

# Create a summary of average budget by project status
status_summary = filtered_df.groupby('Status').agg({'Budget': 'mean', 'Team_Size': 'mean'}).reset_index()

# Plotting the bar chart with improvements
fig = px.bar(
    status_summary,
    x='Status',
    y='Budget',
    title='Average Budget by Project Status',
    labels={'Budget': 'Average Budget'},
    color='Status',
    color_discrete_sequence=px.colors.qualitative.Plotly,  # Use a qualitative color palette
    text='Budget'  # Add data labels
)

# Update layout for better aesthetics
fig.update_layout(
    title_font=dict(size=24),
    xaxis_title='Project Status',
    yaxis_title='Average Budget',
    yaxis_tickprefix="$",  # Add dollar sign to y-axis
    xaxis_tickangle=-45,  # Rotate x-axis labels for better readability
    margin=dict(l=40, r=40, t=40, b=40),  # Adjust margins
)

# Add data labels on top of the bars
fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')

# Display the plot
plotly(fig)