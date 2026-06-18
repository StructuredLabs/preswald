from preswald import text, plotly, connect, get_df, table, selectbox, slider
import pandas as pd
import plotly.express as px

text("# Students Performance Dashboard")

# Load the CSV
connect() 

try:

    def to_camel_case(text):
        words = text.split()
        return " ".join([words[0].capitalize()] + [word if "'s" in word else word.capitalize() for word in words[1:]])

    df = get_df("studentslearning_data")

    df.rename(columns={
        "math score": "Math Score",
        "reading score": "Reading Score",
        "writing score": "Writing Score",
        "parental level of education": "Parental Education",
        "test preparation course": "Test Preparation"
    }, inplace=True)

    df["Test Preparation"] = df["Test Preparation"].str.title()
    df["Parental Education"] = df["Parental Education"].apply(to_camel_case)


  # Interactive Filters
    gender_filter = selectbox("Filter by Gender", ["All"] + df["gender"].unique().tolist())
    parental_edu_filter = selectbox("Filter by Parental Education", ["All"] + df["Parental Education"].unique().tolist())
    test_prep_filter = selectbox("Filter by Test Preparation", ["All"] + df["Test Preparation"].unique().tolist())

    # Math Score Minimum Filter 
    math_score_min = slider(
        "Select the Minimum Math Score to Include in the Charts",
        min_val=int(df["Math Score"].min()),
        max_val=int(df["Math Score"].max()),
        default=int(df["Math Score"].min()),
        size=4
    )

    # Apply Filters
    df_filtered = df.copy()

    if gender_filter != "All":
        df_filtered = df_filtered[df_filtered["gender"] == gender_filter]

    if parental_edu_filter != "All":
        df_filtered = df_filtered[df_filtered["Parental Education"] == parental_edu_filter]

    if test_prep_filter != "All":
        df_filtered = df_filtered[df_filtered["Test Preparation"] == test_prep_filter]

    df_filtered = df_filtered[df_filtered["Math Score"] >= math_score_min]

    # Performance Distribution (Bar Chart)
    df_avg_scores = df_filtered[["Math Score", "Reading Score", "Writing Score"]].mean().reset_index()
    df_avg_scores.columns = ["Subject", "Average Score"]

    fig_avg_scores = px.bar(
        df_avg_scores, x="Subject", y="Average Score", 
        title="Average Performance Across Subjects", 
        text_auto=True, color="Subject"
    )
    plotly(fig_avg_scores)

    # Gender-Based Performance (Grouped Bar Chart)
    df_gender_avg = df_filtered.groupby("gender")[["Math Score", "Reading Score", "Writing Score"]].mean().reset_index()
    df_gender_avg_melted = df_gender_avg.melt(id_vars="gender", var_name="Subject", value_name="Average Score")

    fig_gender_perf = px.bar(
        df_gender_avg_melted, x="Subject", y="Average Score", color="gender", 
        barmode="group", title="Gender-Based Performance Comparison"
    )
    plotly(fig_gender_perf)

    # Parental Education vs. Scores (Box Plot)
    fig_parent_edu = px.box(
        df_filtered, x="Parental Education", y="Math Score", color="Parental Education",
        title="Math Scores by Parental Education Level"
    )
    plotly(fig_parent_edu)


    # Math, Reading, Writing Scores Grouped by Test Preparation Course
    df_test_prep_table = df_filtered.groupby("Test Preparation")[["Math Score", "Reading Score", "Writing Score"]].mean().reset_index()
    df_test_prep_table.columns = ["Test Preparation", "Avg Math Score", "Avg Reading Score", "Avg Writing Score"]

    text("**Average Scores Based on Test Preparation Course:**")
    table(df_test_prep_table)


    text("**Key Insights from Data (After Filtering):**")
    text(f"- **Minimum Math Score Selected:** {math_score_min}", size=1)
    text("- **Use filters & slider** to analyze student performance dynamically.")
    text("- **Subject-wise performance** changes based on score selection.")
    text("- **Gender-based performance trends** help understand learning styles.")
    text("- **Higher parental education levels may correlate with better scores.**")
    text("- **Test preparation courses significantly improve student performance.**")


except Exception as e:
    text(f"**Error:** {str(e)}")