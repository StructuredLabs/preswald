from preswald import text, plotly, connect, get_df, table, slider, text_input
import pandas as pd
import plotly.express as px

text("# AI-Powered Job Market Insights")
text("📊 Explore AI job demand, salary trends, and required skills.")

# Load the CSV
connect()
df = get_df('job_market_data')
if df is None:
    raise ValueError("ERROR: Dataset 'job_market_data' not loaded. Check if the CSV is in the 'data/' folder.")

# Display Top Job Titles
top_jobs = df["Job_Title"].value_counts().head(10).reset_index()
top_jobs.columns = ["Job Title", "Job Count"]
table(top_jobs, title="Top 10 In-Demand Job Titles")

# Salary & Skills Filtering
salary_min = slider("Min Salary", min_val=int(df["Salary_USD"].min()), max_val=int(df["Salary_USD"].max()), default=50000)
salary_max = slider("Max Salary", min_val=int(df["Salary_USD"].min()), max_val=int(df["Salary_USD"].max()), default=200000)

# Extract unique skills from the dataset
skills_list = df["Required_Skills"].explode().dropna().unique().tolist()
search_skill = text_input("🔍 Search for a Skill")

# Apply Filters to Dataset
filtered_df = df[(df["Salary_USD"] >= salary_min) & (df["Salary_USD"] <= salary_max)]
if search_skill:
    filtered_df = df[df["Required_Skills"].astype(str).str.contains(search_skill, case=False, na=False)]

table(filtered_df, title="Filtered Job Listings")


# Visualizations - Salary Distribution
fig_salary = px.histogram(df, x="Salary_USD", nbins=50, title="Salary Distribution", labels={"Salary_USD": "Salary ($USD)"})
plotly(fig_salary)


# Visualizations - Job Demand Over Time
# Check if you have a 'date_posted' column, or use an alternative column like 'Job_Title'
fig_trends = px.line(df.groupby("Job_Title").size().reset_index(), x="Job_Title", y=0, 
                     title="Job Demand Over Time", labels={"Job_Title": "Job Title", "0": "Number of Jobs"})
plotly(fig_trends)


text("**Explore salary trends, demand for AI skills, and job openings dynamically!**")