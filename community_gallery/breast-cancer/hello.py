from preswald import connect, get_df, table, text, checkbox, text_input, alert, slider, selectbox, query, plotly
import pandas as pd
import plotly.express as px

# Load the CSV
connect()  # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')

# Intro section
text("# Breast Cancer Data Analysis and Exploration")
text("""
Breast cancer is one of the most substantial global health concerns for women. This application allows you to explore and analyze a dataset of breast cancer patients obtained from the National Cancer Institute in 2017.
""")
text("---")

# Complex fields description
text("""
**Complex Fields:**

- **T Stage**: Describes the size or extent of the primary tumor (e.g., T1 is a small tumor).
- **N Stage**: Indicates the spread of cancer to nearby lymph nodes (e.g., N1 means spread to some nodes).
- **6th Stage**: Refers to the stage of cancer in the 6th edition of the TNM system (e.g., IIA means localized cancer with some spread).
- **Differentiation**: How much the cancer cells resemble normal cells. Poorly differentiated means more abnormal and aggressive cells.
- **Grade**: Abnormality of tumor cells. Grade 3 means highly abnormal and aggressive.
- **Tumor Size**: The size of the tumor in millimeters.
- **Estrogen Status**: Shows if cancer cells are sensitive to estrogen. "Positive" means they are.
- **Progesterone Status**: Similar to estrogen, but for progesterone sensitivity.
- **Regional Node Examined**: Number of nearby lymph nodes tested for cancer.
- **Regional Node Positive**: Indicates whether cancer has been found in nearby lymph nodes.
""")
text("---")

# Column filters
selected_columns = [col for col in df.columns if checkbox(f"Show {col}")]
df_filtered = df[selected_columns] if selected_columns else df

# Row limit option
limit = None
if checkbox("Limit number of rows"):
    raw_limit = text_input(placeholder="Enter a number to limit rows", label="Row Limit")
    try:
        limit = int(raw_limit)
    except ValueError:
        alert(message="Please enter a valid number", level="error")

# Tumor size filter
if 'Tumor Size' in selected_columns:
    tumor_size = slider(
        label="Select Tumor Size (mm)", 
        min_val=0.0, max_val=100.0, step=1.0, default=50.0
    )
    df_filtered = df_filtered[df_filtered['Tumor Size'] == tumor_size]

# Estrogen status filter
estrogen_status = selectbox("Filter by Estrogen Status", options=["All", "Positive", "Negative"], default="All")
if 'Estrogen Status' in selected_columns and estrogen_status != "All":
        df_filtered = df_filtered[df_filtered['Estrogen Status'] == estrogen_status]

# Grade search filter
grade_search = text_input("Search by Grade")
if 'Grade' in selected_columns and grade_search:
    df_filtered = df_filtered[df_filtered['Grade'].astype(str).str.contains(grade_search, na=False)]

# Display filtered data
table(df_filtered, title="Filtered Breast Cancer Dataset", limit=limit)

# Data analysis section
text("---")
text("## Data Analysis")

# SQL Query for basic statistics
sql = """
SELECT 
    AVG("Tumor Size") AS avg_tumor_size,
    MAX("Tumor Size") AS max_tumor_size,
    MIN("Tumor Size") AS min_tumor_size,
    AVG("Survival Months") AS avg_survival_months
FROM sample_csv
"""
statistics = query(sql, 'sample_csv')
text("### Statistics:")
text(f"**Average Tumor Size**: {statistics['avg_tumor_size'][0]:.2f} mm")
text(f"**Max Tumor Size**: {statistics['max_tumor_size'][0]:.2f} mm")
text(f"**Min Tumor Size**: {statistics['min_tumor_size'][0]:.2f} mm")
text(f"**Average Survival Months**: {statistics['avg_survival_months'][0]:.2f} months")

# SQL Query to get count of Estrogen Status
sql = """
SELECT "Estrogen Status", COUNT(*) AS count
FROM sample_csv
GROUP BY "Estrogen Status"
"""
estrogen_status_count = query(sql, 'sample_csv')
text("### Estrogen Status Distribution:")
for index, row in estrogen_status_count.iterrows():
    estrogen_status = row['Estrogen Status']
    count = row['count']
    text(f"**{estrogen_status}**: {count} patients")

# SQL Query to get count of grade distribution
sql = """
SELECT "Grade", COUNT(*) AS count
FROM sample_csv
GROUP BY "Grade"
"""
grade_count = query(sql, 'sample_csv')
text("### Grade Distribution:")
for index, row in grade_count.iterrows():
    grade = row['Grade']
    count = row['count']
    text(f"**Grade {grade}**: {count} patients")

# SQL Query to find correlation (Tumor Size vs Survival Months) via basic regression analysis
sql = """
SELECT 
    CORR("Tumor Size", "Survival Months") AS tumor_survival_corr
FROM sample_csv
"""
correlation = query(sql, 'sample_csv')
text(f"### Correlation between Tumor Size and Survival Months: {correlation.iloc[0, 0]:.2f}")

# Create plotly scatter plot for tumor size vs survival months
fig = px.scatter(df, x="Tumor Size", y="Survival Months", title="Tumor Size vs Survival Months", labels={
    "Tumor Size": "Tumor Size (mm)",
    "Survival Months": "Survival Months"
})
fig.update_traces(marker=dict(size=8, opacity=0.7, line=dict(width=1, color='DarkSlateGrey')))
fig.update_layout(
    template="plotly_white",
    xaxis_title="Tumor Size (mm)",
    yaxis_title="Survival Months"
)

text("### Tumor Size vs Survival Months")
plotly(fig)
