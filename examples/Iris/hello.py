from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px
import plotly.graph_objects as go


connect()
df = get_df("Iris")

print("Dataset Columns:", df.columns)

sql = "SELECT * FROM Iris WHERE PetalLengthCm > 1.5"
filtered_df = query(sql, "Iris")


text("# Iris Data Analysis App")
table(filtered_df, title="Filtered Iris Data (Petal Length > 1.5)")

threshold = slider("Minimum Petal Length", min_val=0.5, max_val=6.5, default=1.5)
table(df[df["PetalLengthCm"] > threshold], title="Dynamic Iris Data View")

fig_scatter = px.scatter(df, x="SepalLengthCm", y="SepalWidthCm", color="Species")
plotly(fig_scatter)


fig_hist = px.histogram(df, x="PetalLengthCm", nbins=20, color="Species", title="Petal Length Distribution")
plotly(fig_hist)

fig_box = px.box(df, x="Species", y="SepalWidthCm", color="Species", title="Sepal Width Across Species")
plotly(fig_box)


fig_pie = px.pie(df, names="Species", title="Species Distribution")
plotly(fig_pie)


correlation = df.drop(columns=["Species"]).corr()
fig_heatmap = go.Figure(data=go.Heatmap(z=correlation.values, x=correlation.index, y=correlation.columns, colorscale="Viridis"))
fig_heatmap.update_layout(title="Feature Correlation Heatmap")
plotly(fig_heatmap)
