from preswald import text, plotly, connect, get_df, separator, table, slider
import pandas as pd
import plotly.express as px

# Connect to the data source
connect()
df = get_df('student_csv')

# Report Title
text(
    "# Student Depression Data Analysis 📊 \n "
    "This report provides a visual analysis of student depression, "
    "exploring relationships between various factors. \n"
    "The report explores various factors such as **age, academic pressure, sleep duration, work/study hours, and dietary habits**, "
    "and their relationship with **depression levels** among students."
)


# Add gender distribution plot
text("## Gender Distribution")
gender_counts = df['Gender'].value_counts()
gender_fig = px.bar(
    gender_counts, 
    x=gender_counts.index, 
    y=gender_counts.values, 
    title="Gender Distribution", 
    labels={'x': 'Gender', 'y': 'Count'},
    color=gender_counts.index,
    color_discrete_sequence=px.colors.qualitative.Set2
)
plotly(gender_fig)

separator()

# Financial Stress vs. Depression (Bar Graph)
text("## Financial Stress vs. Depression (Bar Graph)")

# Grouping data to count occurrences
stress_depression_counts = df.groupby("Financial Stress")["Depression"].value_counts().unstack()

# Create a bar chart
bar_fig = px.bar(
    stress_depression_counts, 
    barmode="group",  # Group bars side by side
    title="Financial Stress vs. Depression",
    labels={"Financial Stress": "Financial Stress Level", "value": "Count"},
    color_discrete_sequence=["yellow", "blue"]  # Updated to use yellow and blue colors
)

# Update layout for a clean look
bar_fig.update_layout(
    xaxis_title="Financial Stress Level",
    yaxis_title="Number of Students",
    font=dict(family="Arial", size=12),
    plot_bgcolor="rgba(240, 240, 240, 0.5)",  # Light gray background
    title_font_size=16,
    legend_title="Depression Level"
)

plotly(bar_fig)

separator()

# Sleep Duration Distribution
text("## Sleep Duration Distribution")
sleep_counts = df["Sleep Duration"].value_counts()
sleep_fig = px.bar(
    sleep_counts, 
    x=sleep_counts.index, 
    y=sleep_counts.values, 
    title="Sleep Duration Distribution", 
    labels={'x': 'Sleep Duration', 'y': 'Count'},
    color=sleep_counts.index,
    color_discrete_sequence=px.colors.qualitative.Pastel
)
plotly(sleep_fig)

separator()

# Dietary Habits Distribution
text("## Dietary Habits Distribution")
diet_counts = df["Dietary Habits"].value_counts()
diet_fig = px.bar(
    diet_counts, 
    x=diet_counts.index, 
    y=diet_counts.values, 
    title="Dietary Habits Distribution", 
    labels={'x': 'Dietary Habits', 'y': 'Count'},
    color=diet_counts.index,
    color_discrete_sequence=px.colors.qualitative.Safe
)
plotly(diet_fig)

separator()

# Scatter Plot: Work/Study Hours vs. Age with Depression
text("## Relationship Between Work/Study Hours and Age")
scatter_fig = px.scatter(
    df, x='Work/Study Hours', y='Age', color='Depression',
    title="Scatter Plot: Work/Study Hours vs. Age",
    labels={'Work/Study Hours': 'Work/Study Hours', 'Age': 'Age'},
    opacity=0.7,
    color_discrete_map={0: "blue", 1: "orange"},
    template="simple_white"
)
text("This scatter plot visualizes the relationship between work/study hours and age, categorized by depression levels.")
plotly(scatter_fig)

separator()

# Box Plot: CGPA vs. Age with Depression
text("## CGPA Distribution Across Age Groups")
box_fig = px.box(
    df, x='Age', y='CGPA', color='Depression',
    title="Box Plot: CGPA Distribution Across Age Groups",
    labels={'Age': 'Age', 'CGPA': 'Cumulative GPA'},
    color_discrete_map={0: "blue", 1: "orange"},
    template="simple_white"
)
text("This box plot provides insights into CGPA distribution across different age groups, categorized by depression levels.")
plotly(box_fig)

separator()

# Interactive slider for filtering academic pressure
text("## Impact of Academic Pressure on Depression")
pressure_threshold = slider("Select Academic Pressure Threshold", min_val=int(df['Academic Pressure'].min()), max_val=int(df['Academic Pressure'].max()), default=3)
filtered_df = df[df['Academic Pressure'] >= pressure_threshold]
table(filtered_df, title="Filtered Data Based on Academic Pressure")