from preswald import connect, get_df, table, text, plotly, slider
import plotly.express as px

# Initialize connection and load dataset
connect()
df = get_df("alzheimers_disease_data")

# Display title
text("# Alzheimer's Disease Data Explorer 🧠")
text("""
This dashboard helps visualize Alzheimer's disease-related patient data.  
- **MMSE Score (Mini-Mental State Exam)** is a test used to assess cognitive function.
- Use the **slider** to filter patients by MMSE Score and explore cognitive performance trends.
- Interactive **charts** reveal patterns across age, diagnosis types, cholesterol levels, and behavioral issues.
- View a **filtered table** of patient data to assist with clinical or research insights.
""")


# Histogram: MMSE Score Distribution
fig_mmse = px.histogram(
    df,
    x="MMSE",
    nbins=20,
    title="Distribution of MMSE Scores",
    labels={"MMSE": "Mini-Mental State Examination Score"},
    opacity=0.75
)
plotly(fig_mmse)

# Scatter Plot: Age vs. Cholesterol Levels
fig_chol = px.scatter(
    df,
    x="Age",
    y="CholesterolTotal",
    color="Diagnosis",
    title="Age vs. Cholesterol Levels",
    labels={"CholesterolTotal": "Total Cholesterol Level"}
)
plotly(fig_chol)

# User Control: MMSE Score Threshold
threshold = slider(
    "Minimum MMSE Score",
    min_val=int(df["MMSE"].min()),
    max_val=int(df["MMSE"].max()),
    default=20
)

# Filter data based on MMSE Score
filtered_df = df[df["MMSE"] >= threshold]

# Scatter plot: Age vs. MMSE Score by Diagnosis
fig = px.scatter(
    filtered_df,
    x="Age",
    y="MMSE",
    color="Diagnosis",
    title=f"Age vs MMSE Score (MMSE ≥ {threshold})",
    labels={"Diagnosis": "Diagnosis Type"}
)
plotly(fig)

# Bar Chart: Diagnosis vs. Behavioral Problems
fig_behavior = px.bar(
    df,
    x="Diagnosis",
    y="BehavioralProblems",
    color="Diagnosis",
    title="Behavioral Problems Across Diagnosis Types",
    labels={"BehavioralProblems": "Behavioral Issues Score"}
)
plotly(fig_behavior)

# Display filtered data table
table(
    filtered_df[["PatientID", "Age", "MMSE", "Diagnosis",
                 "FunctionalAssessment", "CholesterolTotal"]],
    title="Filtered Patient Data"
)
