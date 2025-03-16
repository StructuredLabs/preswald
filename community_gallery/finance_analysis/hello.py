from preswald import text, plotly, connect, get_df, table, query, slider  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore

text("# Finance Data Analysis")
text("Finance Data Analysis Example")

# Load the CSV
connect()  # Load in all sources, which by default is the sample_csv
df = get_df("Finance_data")
table(df, title="Full Finance Data")

# Query the data: Filter only Male
sql = "SELECT * FROM Finance_data WHERE gender = 'Male'"
filtered_df = query(sql, "Finance_data")
table(filtered_df, title="Filtered: Only Male Data")

# Sort Data based on Fixed_Deposits
sql = "SELECT * FROM Finance_data ORDER BY Fixed_Deposits DESC"
sorted_df = query(sql, "Finance_data")
table(sorted_df, title="Sorted: Fixed_Deposits Descending")

# Slider Example: Dynamic Filter (assuming 'age' or 'Mutual_Funds' column as numeric)
threshold = slider("Threshold for Mutual Funds", min_val=0, max_val=10, default=5)
filtered_slider_df = df[df["Mutual_Funds"] > threshold]
table(filtered_slider_df, title="Filtered: Mutual Funds > Threshold")

# create visulaization
fig = px.scatter(
    df,
    x="Fixed_Deposits",
    y="Mutual_Funds",
    title="Scatter Plot: Fixed Deposits vs Mutual Funds",
    labels={
        "Fixed_Deposits": "Fixed Deposits (in Units)",
        "Mutual_Funds": "Mutual Funds Investment",
    },
)
fig.update_layout(
    xaxis_title="Fixed Deposits (in Units)",
    yaxis_title="Mutual Funds Investment",
    title_x=0.5,  # Center the title
)
plotly(fig)
