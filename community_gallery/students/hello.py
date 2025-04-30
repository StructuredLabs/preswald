from preswald import connect, get_df, text, table, slider, selectbox, plotly
import pandas as pd
import plotly.express as px

# Step 1: Load the dataset
csv_path = "data/student.csv"  # Ensure this path is correct
df = pd.read_csv(csv_path)

# Step 2: Build the UI
text("# Advanced Student Performance Analysis App")

# Add interactive controls
min_attendance = slider("Minimum Attendance (%)", min_val=0, max_val=100, default=80)
min_score = slider("Minimum Score", min_val=0, max_val=100, default=70)

# Create a dropdown for selecting a subject using selectbox
subjects = df["Subject"].unique().tolist()
selected_subject = selectbox("Select Subject", options=subjects, default="Math")

# Create a dropdown for selecting a gender using selectbox
genders = ["All"] + df["Gender"].unique().tolist()
selected_gender = selectbox("Select Gender", options=genders, default="All")

# Step 3: Filter the dataset based on user inputs
filtered_df = df[
    (df["Attendance"] >= min_attendance) &
    (df["Score"] >= min_score) &
    (df["Subject"] == selected_subject)
]

if selected_gender != "All":
    filtered_df = filtered_df[filtered_df["Gender"] == selected_gender]

# Display the filtered data
text(f"### Filtered Data (Subject: {selected_subject}, Gender: {selected_gender})")
table(filtered_df, title="Filtered Students")

# Step 4: Create visualizations
# Visualization 1: Score distribution by gender
fig1 = px.histogram(filtered_df, x="Score", color="Gender", nbins=10, title="Score Distribution by Gender")
plotly(fig1)

# Visualization 2: Attendance vs. Score scatter plot
fig2 = px.scatter(filtered_df, x="Attendance", y="Score", color="Grade", title="Attendance vs. Score")
plotly(fig2)