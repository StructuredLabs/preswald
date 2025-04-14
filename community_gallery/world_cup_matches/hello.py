from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

text("# Sebastian Castro Ochoa!")
text("My first preswald app. 🎉")

# Load the CSV
connect()
df = get_df("WorldCupMatches_csv")


sql = "SELECT Year,Stadium,City,Attendance FROM WorldCupMatches_csv"
filtered_df = query(sql, "WorldCupMatches_csv")


text("# My Data Analysis App")
table(filtered_df, title="Filtered Data")

threshold = slider("Threshold", min_val=0, max_val=4000, default=50)
table(filtered_df[filtered_df["Attendance"] > threshold], title="Dynamic Data View")

fig = px.scatter(filtered_df, x="Stadium", y="Attendance", color="City")
plotly(fig)
