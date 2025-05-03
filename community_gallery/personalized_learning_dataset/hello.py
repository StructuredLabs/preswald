from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

# defining a color palette for consistency 
color_palette = px.colors.qualitative.Set2

text(""" 
# 📊 Student Learning & Performance Dashboard
### *Insights into student performance, behavior, and learning preferences*
""")

# 1. LOAD THE DATA SET
connect()
df = get_df("personalized_learning_dataset")
text(f"Analysis based on data from **{len(df)}** students across **{df['Course_Name'].nunique()}** courses.")




# 2. QUERY OR MANIPULATE THE DATA 
avg_score = query("SELECT ROUND(AVG(Quiz_Scores), 1) AS avg_score FROM personalized_learning_dataset", 
                  "personalized_learning_dataset").iloc[0]['avg_score']

avg_time = query("SELECT ROUND(AVG(Time_Spent_on_Videos), 1) AS avg_time FROM personalized_learning_dataset", 
                 "personalized_learning_dataset").iloc[0]['avg_time']

top_course_result = query("""
SELECT Course_Name, ROUND(AVG(Quiz_Scores), 1) AS avg_score
FROM personalized_learning_dataset
GROUP BY Course_Name
ORDER BY avg_score DESC
LIMIT 1
""", "personalized_learning_dataset")
top_course = top_course_result.iloc[0]['Course_Name']

pass_rate = query("""
SELECT ROUND(
    (COUNT(CASE WHEN Quiz_Scores >= 70 THEN 1 END) * 100.0) / COUNT(*),
    1
) AS pass_rate
FROM personalized_learning_dataset
""", "personalized_learning_dataset").iloc[0]['pass_rate']

kpi_df = pd.DataFrame({
    "Metric": ["Average Quiz Score", "Average Time on Videos (min)", "Top Performing Course", "Pass Rate (≥70%)"],
    "Value": [f"{avg_score}/100", f"{avg_time} minutes", top_course, f"{pass_rate}%"]
})

text("## 🎯 Learning Insights Summary")
table(kpi_df, title="📌 Key Performance Metrics")



# 4. CREATE A VISUALIZATION
text("## 🔗 Time Investment vs. Performance")

fig_corr = px.scatter(df, x="Time_Spent_on_Videos", y="Quiz_Scores", 
                     color="Course_Name", size="Quiz_Attempts",
                     hover_data=["Age", "Education_Level", "Learning_Style"],
                     title="Relationship Between Time Spent and Quiz Scores",
                     labels={"Time_Spent_on_Videos": "Time Spent on Videos (minutes)",
                            "Quiz_Scores": "Quiz Score"},
                     color_discrete_sequence=color_palette)

fig_corr.update_layout(
    height=500,
    template="plotly_white"
)
fig_corr.add_shape(
    type="line", line=dict(dash="dash", color="red"),
    y0=70, y1=70, x0=0, x1=df["Time_Spent_on_Videos"].max()
)
fig_corr.add_annotation(
    x=df["Time_Spent_on_Videos"].max()*0.95, y=72,
    text="Passing Score (70)",
    showarrow=False,
    font=dict(color="red")
)

plotly(fig_corr)

# 3. BUILD AN INTERACTIVE UI
text("## 🔎 Interactive Student Explorer")
text("Adjust the minimum quiz score threshold to identify high and low performers:")

score_threshold = slider("Quiz Score Threshold", min_val=0, max_val=100, default=70)

high_performers = df[df["Quiz_Scores"] >= score_threshold].sort_values("Quiz_Scores", ascending=False)

if len(high_performers) > 0:
    text(f"### Students scoring {score_threshold} or higher ({len(high_performers)} students)")
    table(high_performers[["Student_ID", "Age", "Gender", "Education_Level", 
                         "Learning_Style", "Course_Name", "Quiz_Scores"]], 
         title="")
else:
    text(f"No students scored {score_threshold} or higher.")
