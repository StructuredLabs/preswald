from preswald import text, plotly, connect, get_df, table, slider
import plotly.express as px



text("# AI-Powered Job Recommendations")
text("This report visualizes data about **50,000 job postings** spanning multiple industries, locations, experience levels, and salary brackets. Use the interactive features below to explore the data.")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')
min_salary = df["Salary"].min()
max_salary = df["Salary"].max()

# Query or manipulate the data
text("## Filter Jobs by Salary")
threshold = slider("Threshold", min_val=min_salary, max_val=max_salary, default=(min_salary + max_salary) // 2)
filtered_data = df[df["Salary"] > threshold]

text("### Filtered Job Data")
table(filtered_data, title="Filtered Salary Data View")

# Feature 3: Plotting
text("## Job Title vs. Salary")
fig = px.scatter(df, x="Salary", y="Job Title", title="Job Title vs. Salary", hover_name="Experience Level")
plotly(fig)

# Pie Chart: Distribution of Jobs by Experience Level
text("## Job Distribution by Experience Level")
experience_distribution = filtered_data["Experience Level"].value_counts().reset_index()
experience_distribution.columns = ["Experience Level", "count"]
fig = px.pie(experience_distribution, labels="Experience Level", values="count", title="Job Distribution by Experience Level", hover_name="Experience Level")
plotly(fig)

# Bar Plot: Top Companies by Job Postings
text("## Top Companies by Job Postings")
company_counts = filtered_data["Company"].value_counts().reset_index()
company_counts.columns = ["Company", "count"]
fig = px.bar(company_counts, x="Company", y="count", title="Top Companies by Job Postings")
plotly(fig)