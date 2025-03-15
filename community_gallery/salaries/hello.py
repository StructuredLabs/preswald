from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px
from preswald import query


text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect()  # load in all sources, which by default is the sample_csv
df = get_df("salaries")

# Show the data
table(df.head())

sql = "SELECT * FROM salaries WHERE Salary_in_usd >= 50000"
filtered_df = query(sql, "salaries")


# Distribution of salaries by experience level
fig_exp = px.box(
    df,
    x="experience_level",
    y="salary_in_usd",
    title="Salary Distribution by Experience Level",
    labels={"experience_level": "Experience Level", "salary_in_usd": "Salary (USD)"},
)
plotly(fig_exp)

# Salaries across job titles (top 10 highest median salaries)
top_jobs = (
    df.groupby("job_title")["salary_in_usd"]
    .median()
    .sort_values(ascending=False)
    .head(10)
    .index
)
data_top_jobs = df[df["job_title"].isin(top_jobs)]
fig_jobs = px.box(
    data_top_jobs,
    x="salary_in_usd",
    y="job_title",
    orientation="h",
    title="Top 10 Job Titles by Median Salary",
    labels={"salary_in_usd": "Salary (USD)", "job_title": "Job Title"},
)
plotly(fig_jobs)

# Salaries based on company size
fig_company = px.violin(
    df,
    x="company_size",
    y="salary_in_usd",
    box=True,
    title="Salary Distribution by Company Size",
    labels={"company_size": "Company Size", "salary_in_usd": "Salary (USD)"},
)
plotly(fig_company)
