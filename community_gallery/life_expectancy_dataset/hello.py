from preswald import text, plotly, query, connect, get_df, table, slider
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('life_expectancy_dataset')

#query the data

sql = "SELECT * FROM life_expectancy_dataset WHERE year >= 1998 AND year <= 2000 AND region = 'ASIA'"
filtered_df = query(sql, "life_expectancy_dataset")

# display the data

text("# My Data Analysis App")
table(filtered_df, title="Filtered Data")


threshold = slider("Threshold", min_val=1990, max_val=2000, default=1995)
table(df[df["year"] == threshold], title="Dynamic Data View")

df[['life_expectancy_men_min','life_expectancy_men_max']] = df['life_expectancy_men'].str.split(',',expand=True)

fig = px.scatter(df, x="year", y="life_expectancy_men_min", color="year")
plotly(fig)