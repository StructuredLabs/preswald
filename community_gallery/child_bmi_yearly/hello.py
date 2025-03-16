from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

# Title and Introduction
text("# Welcome to Josh McCormack's Code Assessment for Structured Labs!")
text("This application visualizes Child BMI Data by comparing different BMI categories across school years.")

# Connect to the database and load the data
connect()  
df = get_df('bmidata')  # Load the full dataset

# Display the complete unfiltered data
table(df, title="All Data")

# Filter the data using a SQL query
sql = "SELECT SchoolYear, NameHospital, Sex, EpiUnderweight, EpiHealthyWeight, EpiOverweight, EpiObese FROM bmidata"
filtered_df = query(sql, "bmidata")
text("## Filtered BMI Data (2001-2023)")
table(filtered_df, title="Filtered Data")

# Transform the data into long format to compare BMI categories side by side
df_long = pd.melt(filtered_df, 
                  id_vars=['SchoolYear'], 
                  value_vars=['EpiUnderweight', 'EpiHealthyWeight', 'EpiOverweight', 'EpiObese'],
                  var_name='BMI_Category', 
                  value_name='Value')

# Aggregate the data by SchoolYear and BMI_Category (averaging in case there are multiple records per year)
aggregated_df = df_long.groupby(['SchoolYear', 'BMI_Category'], as_index=False).mean()

# Ensure that SchoolYear values are Python ints to avoid JSON serialization issues
aggregated_df['SchoolYear'] = aggregated_df['SchoolYear'].astype(int)

# Create a grouped bar chart showing the average BMI distribution across school years
fig_overall = px.bar(aggregated_df, 
                     x='SchoolYear', 
                     y='Value', 
                     color='BMI_Category',
                     barmode='group',
                     title='Average Child BMI Distribution Across School Years',
                     labels={'Value': 'Average BMI Percentage', 'SchoolYear': 'School Year'})
plotly(fig_overall)

# Create a line chart that connects the average values over time for each BMI category.
fig_line = px.line(aggregated_df, 
                   x='SchoolYear', 
                   y='Value', 
                   color='BMI_Category',
                   markers=True,
                   title='Trend of Average Child BMI Categories Over Time',
                   labels={'Value': 'Average BMI Percentage', 'SchoolYear': 'School Year'})
plotly(fig_line)

# Add a slider to dynamically update the chart for a selected school year
min_year = int(aggregated_df['SchoolYear'].min())
max_year = int(aggregated_df['SchoolYear'].max())
default_year = min_year  # Default slider value

# Cast the slider result to a Python int
selected_year = int(slider("School Year Selector", min_val=min_year, max_val=max_year, default=default_year))
year_data = aggregated_df[aggregated_df['SchoolYear'] == selected_year]

fig_year = px.bar(year_data, 
                  x='BMI_Category', 
                  y='Value',
                  title=f'BMI Distribution for School Year {selected_year}',
                  labels={'Value': 'Average BMI Percentage', 'BMI_Category': 'BMI Category'})
plotly(fig_year)

# Display the aggregated data as a table for further inspection
table(aggregated_df, title="Aggregated BMI Data by School Year and Category")
