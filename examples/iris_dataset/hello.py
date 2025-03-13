from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('iris_csv')

# query the data
sql = "SELECT * FROM iris_csv WHERE variety = 'Setosa'"
filtered_df = query(sql, "iris_csv")

# build an interactive UI
text("# Iris Dataset Analysis App")
table(filtered_df, title="Filtered Data: Setosa Variety")

# add user controls
threshold = slider("Sepal Length", min_val=4, max_val=8, step=1, default=6)
table(df[df["sepal.length"] > threshold], title="Dynamic Sepal Length")

# create a visualization
text("## Sepal Length vs Sepal Width")
fig = px.scatter(df, x="sepal.length", y="sepal.width", labels={"sepal.length": "Sepal Length", "sepal.width": "Sepal Width"})
plotly(fig)
