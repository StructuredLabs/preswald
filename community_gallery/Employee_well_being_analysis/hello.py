
from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px

connect() # Initialize connection to preswald.toml data sources

# Load the dataset
df = get_df("Impact_of_Remote_Work_on_Mental_Health_csv")  # Load data

# Query or manipulate the data 
# select employees with "High" stress levels
sql = "SELECT * FROM Impact_of_Remote_Work_on_Mental_Health_csv WHERE Stress_Level = 'High'"
filtered_df = query(sql, "Impact_of_Remote_Work_on_Mental_Health_csv")

# Build an interactive UI
text("# Employee Well-being Analysis")
table(filtered_df, title="High Stress Employees")

# Slider for filtering based on Hours Worked Per Week
threshold = slider("Minimum Hours Worked Per Week", min_val=20, max_val=60, default=40)
# Display the dynamically filtered table
table(df[df["Hours_Worked_Per_Week"] > threshold], title="Employees Working More Than Threshold Hours")

# Create a scatter plot for Work-Life Balance Rating vs. Hours Worked Per Week
fig = px.scatter(
    df, 
    x="Hours_Worked_Per_Week", 
    y="Age", 
    color="Satisfaction_with_Remote_Work", 
    labels={
        "Hours_Worked_Per_Week": "Hours Worked Per Week", 
        "Age": "Employee Age"
    },
    title="Scatter Plot of Hours Worked vs Age"
)


plotly(fig)



