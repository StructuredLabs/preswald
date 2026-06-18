from preswald import text, plotly, connect, get_df, table, slider, query
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect()  # load in all sources, which by default is the sample_csv
df = get_df('global_water_consumption_csv')


sql = "SELECT * FROM global_water_consumption_csv WHERE country LIKE 'India' limit(10)"
filtered_df = query(sql, "global_water_consumption_csv")

text("# My Data Analysis App")
table(filtered_df, title="Filtered Data")


fig = px.scatter(filtered_df, x='Year', y='Total Water Consumption (Billion Cubic Meters)', text='Country',
                 title='Year vs. Country',
                 labels={'Year': 'Year', 'Country': 'Country'})
plotly(fig)

# Show the data
# table(df)