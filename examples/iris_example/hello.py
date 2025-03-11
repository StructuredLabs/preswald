
from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('iris_csv')

sql = "SELECT * FROM iris_csv WHERE \"sepal.length\" > 5"
filtered_df = query(sql, "iris_csv")

text("# My Data Analysis App")
table(filtered_df, title="Filtered Data")

# Create a scatter plot
fig = px.scatter(df, x='sepal.length', y='sepal.width', text='variety',
                 title='Iris Dataset: Sepal Length vs Width',
                 labels={'sepal.length': 'Sepal Length (cm)', 
                        'sepal.width': 'Sepal Width (cm)',
                        'variety': 'Species'})

threshold = slider("Sepal Length Threshold", min_val=0, max_val=8, default=5)
table(df[df["sepal.length"] > threshold], title="Dynamic Data View")

fig = px.scatter(df, x="sepal.length", y="sepal.width", color="variety")
plotly(fig)
