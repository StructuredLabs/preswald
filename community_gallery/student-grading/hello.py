from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px

# Initialize connection to preswald.toml data sources
connect()

# Load the dataset
df = get_df("Students_Grading_Dataset")
 
# Query and manipulate the dataset
sql = "SELECT * FROM Students_Grading_Dataset WHERE Participation_Score > 5"
pre_filtered_df = query(sql, "Students_Grading_Dataset")

# Display a title for the app
text("# Student Grades Analysis App")

# Add a slider for user input to filter data based on attendance percentage
attendance_threshold = slider("Minimum Attendance (%)", min_val=0, max_val=100, default=50)

# Filter students based on attendance threshold using pandas
filtered_df = pre_filtered_df[pre_filtered_df["Attendance (%)"] >= attendance_threshold]

# Create a scatter plot of Final Score vs. Study Hours per Week
fig = px.scatter(filtered_df, 
                 x="Study_Hours_per_Week", 
                 y="Final_Score", 
                 color="Grade",
                 title="Final Score vs. Study Hours per Week",
                 labels={"Study_Hours_per_Week": "Study Hours per Week", 
                        "Final_Score": "Final Score"})

# Display the scatter plot
plotly(fig)

# Display the filtered data in a table
table(filtered_df, title="Students with Sufficient Attendance")
