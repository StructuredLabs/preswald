import plotly.express as px
from preswald import connect, get_df, table, text, slider, plotly

# Connect to the dataset
connect()
df = get_df("co2_csv")  # Ensure co2.csv is placed in the `data/` folder

from preswald import query
 
sql = "SELECT * FROM my_dataset WHERE Year > 1977"
filtered_df = query(sql, "my_dataset")

# Display Title and Introduction
text("# Global CO2 Emissions Analysis")
text("This app analyzes historical trends in CO2 emissions, GDP, and population.")

threshold = slider("Select the year", min_val=1977, max_val=2022, default=1977)
table(df[df["Year"] > threshold], title="Global CO2 Emissions")

# Bar Chart: CO2 emissions by year
text("## CO2 Emissions Comparison by Year")
fig1 = px.bar(df, x="Year", y="Fossil CO2 Emissions (tons)", title="Yearly CO2 Emissions")
plotly(fig1)

# Line Chart: CO2 emissions over time
text("## CO2 Emissions Over Time")
fig2 = px.line(df, x="Year", y="Fossil CO2 Emissions (tons)", title="Global CO2 Emissions Trend")
plotly(fig2)

# Scatter Plot: Relationship between GDP and CO2 emissions
text("## Relationship Between GDP and CO2 Emissions")
fig3 = px.scatter(df, x="Year", y="GDP Real (USD)", color="Fossil CO2 Emissions (tons)", title="GDP vs CO2 Emissions")
plotly(fig3)
