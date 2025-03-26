from preswald import text, plotly, connect, get_df, table, query, slider, sidebar
import pandas as pd
import plotly.express as px

text("# Average Salary by Job Classification on Montgomery County of Maryland.")

# Load the CSV
connect()  # load in all sources, which by default is the sample_csv
df = get_df("sample_csv")

sidebar(defaultopen=False)

text("# Top 10 Job position with highest average base salary.", size=0.1)
top_10_df_sql = """
    select *
    from sample_csv
    order by cast(replace(replace("Average Of Base Salary", '$', ''), ',', '') as integer) desc limit 10;
"""
top_10_df = query(top_10_df_sql, "sample_csv")
# Create a scatter plot
top_10_fig = px.scatter(
    top_10_df,
    x="Position Title",
    y="Average of Base Salary",
    text="Average of Base Salary",
    title="Position vs. Average Base Salary",
    labels={"quantity": "Quantity", "value": "Value"},
)
# Add labels for each point
top_10_fig.update_traces(
    textposition="top center", marker=dict(size=12, color="lightblue")
)
# Style the plot
top_10_fig.update_layout(template="plotly_white")
# Show the plot
plotly(top_10_fig)

text("# Bottom 10 Job position with lowest average base salary.", size=0.1)
bottom_10_df_sql = """
    select *
    from sample_csv
    order by cast(replace(replace("Average Of Base Salary", '$', ''), ',', '') as integer) limit 10;
"""
bottom_10_df = query(bottom_10_df_sql, "sample_csv")
# Create a scatter plot
bottom_10_fig = px.scatter(
    bottom_10_df,
    x="Position Title",
    y="Average of Base Salary",
    text="Average of Base Salary",
    title="Position vs. Average Base Salary",
    labels={"quantity": "Quantity", "value": "Value"},
)
# Add labels for each point
bottom_10_fig.update_traces(
    textposition="top center", marker=dict(size=12, color="lightblue")
)
# Style the plot
bottom_10_fig.update_layout(template="plotly_white")
# Show the plot
plotly(bottom_10_fig)

# Show the data
threshold = slider(
    "Average Base Salary Greater than", min_val=30000, max_val=250000, default=30000
)
sorted_data_sql = """
    select *, cast(replace(replace("Average of Base Salary", '$', ''), ',', '') as integer) as "Numeric Average Of Base Salary"
    from sample_csv
    order by cast(replace(replace("Average Of Base Salary", '$', ''), ',', '') as integer);
"""
sorted_data = query(sorted_data_sql, "sample_csv")
table(
    sorted_data[sorted_data["Numeric Average Of Base Salary"] > threshold],
    title="Full Data",
)
