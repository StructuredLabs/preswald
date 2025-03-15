from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

text("# Iris data Analysis App")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('iris_csv')

sql = "SELECT * FROM iris_csv WHERE sepal_length > 6.0"
filtered_df = query(sql, "iris_csv")
    
threshold = slider("Sepal Length", min_val=0, max_val=8, default=6)
filtered_data = df[df["sepal_length"] > threshold]
table(filtered_data, title="Dynamic Data View")

fig = px.scatter(df, x="sepal_length", y="sepal_width", color="species")
plotly(fig)
