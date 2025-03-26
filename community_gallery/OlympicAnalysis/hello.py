from preswald import text, plotly, connect, get_df, table,query,slider
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('Olympics')

# df = pd.read_csv("data/Olympics.csv")


sql = "SELECT * FROM Olympics WHERE Year > 2012"
filtered_df = query(sql, "Olympics")


text("# My Data Analysis App")
table(filtered_df, title="Filtered Data")


if all(col in df.columns for col in ["Year", "Total", "NOC"]):
    fig = px.scatter(df, x="Year", y="Total", color="NOC", title="Olympic Medal Count Over Time")
    plotly(fig)
else:
    text("Error: Columns 'Year', 'Total', or 'NOC' not found in dataset!")