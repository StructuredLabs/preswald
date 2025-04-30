from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

# Load the CSV
connect()
df = get_df("groceries")

sql = "SELECT * FROM groceries WHERE Inventory_Turnover_Rate > 50"
filtered_df = query(sql, "groceries")


text("# Grocery Inventory Data Analysis App")
table(filtered_df, title="Filtered Data")

threshold = slider("Threshold", min_val=0, max_val=100, default=50)
table(
    df[df["Inventory_Turnover_Rate"] > threshold],
    title="Dynamic Data View",
)

fig = px.scatter(df, x="Unit_Price", y="Inventory_Turnover_Rate", color="Category")
plotly(fig)
