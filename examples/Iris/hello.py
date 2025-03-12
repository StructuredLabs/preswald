from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px

connect()
df = get_df("Iris") 


print("Dataset Columns:", df.columns)


sql = "SELECT * FROM Iris WHERE PetalLengthCm > 1.5" 
filtered_df = query(sql, "Iris")

text("# Iris Data Analysis App")
table(filtered_df, title="Filtered Iris Data (Petal Length > 1.5)")

threshold = slider("Minimum Petal Length", min_val=0.5, max_val=6.5, default=1.5)
table(df[df["PetalLengthCm"] > threshold], title="Dynamic Iris Data View")

fig = px.scatter(df, x="SepalLengthCm", y="SepalWidthCm", color="Species") 
plotly(fig)


