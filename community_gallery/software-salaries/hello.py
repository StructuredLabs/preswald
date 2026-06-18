from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px

connect()
df = get_df("salary_cvs")

# Create a SQL query to filter the data
sql = "SELECT * FROM salary_cvs WHERE Salary > 500000 AND Rating > 4.5"
filtered_df = query(sql, "salary_cvs")

text("# Salary Analysis App for Jobs with High Salary and Rating above 4.5")

# Add interactive controls
threshold = slider("Higher Salary Threshold", min_val=500000, max_val=1500000, default=500000)
table(filtered_df[filtered_df["Salary"] > threshold], title="Jobs Above Threshold")

# Create a visualization
fig = px.scatter(filtered_df[filtered_df["Salary"] > threshold], x="Rating", y="Salary", color="Job Roles", 
                hover_data=["Company Name", "Location"])
plotly(fig)
