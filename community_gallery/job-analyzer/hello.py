from preswald import text, plotly, connect, get_df, table, slider, selectbox, query
import plotly.express as px


connect()
df = get_df("job_csv")

text("## Job Trends Analyzer!!")
intro_report = """
### Welcome to the Job Trends Analyzer dashboard! This tool helps you explore and 
analyze job statistics across various companies for the year *2023*.
As a proof of concept, only data from the first **15** days has been loaded to meet memory constraints.
Features:
- **Apply** filters to refine and explore specific job trends.
- **Visualize** hiring trends across companies.
- **Analyze** in-demand roles through insightful plots and statistics.

"""
text(intro_report)

# Step 1: Build the sliders for adjusting the salary and company size
step_1_report = """
#### Step 1: Set Your Preferences
Use the sliders to adjust your expected annual 
salary and preferred company size.
"""
text(step_1_report)
min_salary = slider(
    "Choose the minimum desired annual salary in USD (in thousands)",
    min_val=55,
    max_val=65,
    step=1,
    default=55,
)


max_salary = slider(
    "Choose the maximum desired annual salary in USD (in thousands). \
        Should be greater than minimum!!",
    min_val=80,
    max_val=130,
    step=1,
    default=110,
)


company_size = slider(
    "Select the minimum size of the company",
    min_val=12000,
    max_val=140000,
    step=500,
    default=20000,
)

assert min_salary is not None and company_size is not None
# Step 2: Build the checkboxes for selecting the type of work and the country
step_2_report = """
#### Step 2: Filter Country and Type of work  
Apply additional filters to narrow down job opportunities based on location, and role type.
"""
text(step_2_report)
available_countries = df["Country"].unique()
available_work_type = df["Work Type"].unique()

country_box = selectbox(
    "Pick a country from the drop-down",
    options=available_countries.tolist(),
    default="USA",
)

work_type_box = selectbox(
    "Select the desired work-type",
    options=available_work_type.tolist(),
    default="Full-Time",
)

# Step 3: Get the information based on the applied filters
sql_query = f"""
SELECT * FROM job_csv
WHERE "Country"='{country_box}' AND
"Work Type"='{work_type_box}' AND
"Company Size" >= {company_size} AND 
"Min Salary" > {min_salary} AND 
"Max Salary" < {max_salary}
"""
filtered_df = query(sql_query, "job_csv")
filtered_df.drop("column0", inplace=True, axis=1)
display_df = filtered_df.rename(
    columns={
        "Max Salary": "Max Salary (in thousands)",
        "Min Salary": "Min Salary (in thousands)",
    }
)

assert filtered_df is not None
text("### Filtered Job Information")
table(display_df, "Job Statistics for Jan-2023")

# Step 4: Get visualisations
step_4_report = """
## Visualization  
In this section, we will explore data visually using the Plotly library, 
enabling interactive and insightful representations."
"""
# a).
# Company wise pie-chart
available_companies = df["Company"].unique().tolist()
company_box = selectbox(
    "Select a company from the drop-down", options=available_companies, default="Ball"
)

filtered_df = df.groupby(["Company", "Job Title"]).count().unstack(0)
filtered_df = filtered_df.fillna(0)
filtered_df.columns = filtered_df.columns.droplevel(0)
filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated()].reset_index()
assert filtered_df is not None

fig = px.pie(
    filtered_df,
    names="Job Title",
    values=f"{company_box}",
    title=f"(Pie-chart) Role distribution at {company_box}",
)

fig.update_traces(textinfo="none")
plotly(fig)

# b).
# Company wise histogram
fig = px.histogram(
    filtered_df[filtered_df[company_box] != 0],
    x="Job Title",
    y=f"{company_box}",
    title=f"(Histogram) Role distribution at {company_box}",
)


plotly(fig)
