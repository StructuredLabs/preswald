from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

text("# First Demo Project!")
text("Aims to show Water Consumption of various countries since 2015")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('global_water_consumption_csv')



sql = """
SELECT Country, Year, 
       SUM("Total Water Consumption (Billion Cubic Meters)") AS "Total Water Consumption (Billion Cubic Meters)", 
       AVG("Per Capita Water Use (Liters per Day)") AS "Per Capita Water Use (Liters per Day)", 
       MAX("Water Scarcity Level") AS "Water Scarcity Level",
       AVG("Agricultural Water Use (%)") AS "Agricultural Water Use (%)",
       AVG("Industrial Water Use (%)") AS "Industrial Water Use (%)",
       AVG("Household Water Use (%)") AS "Household Water Use (%)",
       AVG("Rainfall Impact (Annual Precipitation in mm)") AS "Rainfall Impact (Annual Precipitation in mm)",
       AVG("Groundwater Depletion Rate (%)") AS "Groundwater Depletion Rate (%)"
FROM global_water_consumption_csv 
WHERE Year > 2014 
GROUP BY Country, Year
ORDER BY Country, Year
"""

filtered_df = query(sql, "global_water_consumption_csv")


fig1 = px.bar(filtered_df, x='Country', y='Total Water Consumption (Billion Cubic Meters)', color='Water Scarcity Level',
              title='Total Water Consumption by Country',
              labels={'Total Water Consumption': 'Total Water Consumption (Billion m³)'},
              color_discrete_sequence=px.colors.qualitative.Pastel)
plotly(fig1)

fig2 = px.line(filtered_df, x='Year', y='Total Water Consumption (Billion Cubic Meters)', color='Country',
               title='Water Consumption Trend Over the Years',
               color_discrete_sequence=px.colors.qualitative.Vivid,
               markers=True)
plotly(fig2)

fig3 = px.pie(filtered_df, names='Water Scarcity Level', title='Distribution of Water Scarcity Levels')
plotly(fig3)

table(filtered_df)

