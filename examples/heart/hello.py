import plotly.express as px
from preswald import connect, get_df, plotly, table, text, slider
import pandas as pd

# Report Title
text(
    """# Heart Disease Analysis with Preswald \n
This report explores factors related to heart disease using clinical data. 
Visualizations compare health metrics between patients with (num=1) and without (num=0) heart disease."""
)

# Load dataset
connect()  # Loads heart.csv by default
df = get_df("heart_csv")

# Convert 'num' to categorical for better legend
df['diagnosis'] = df['num'].map({0: 'No Disease', 1: 'Disease'})


def show_full_screen(fig):
    fig.show()


# 1. Scatter plot - Age vs Cholesterol
text(
    """## Age vs Cholesterol Levels \n
This scatter plot examines the relationship between age and cholesterol levels. 
Patients with heart disease tend to cluster in higher cholesterol ranges across all ages."""
)

age = slider("Age", min_val=45, max_val=65, default=48)

filtered_df = df[(df["age"] <= age)]

fig1 = px.scatter(
    filtered_df,
    x="age",
    y="chol",
    color="diagnosis",
    title="Age vs Cholesterol",
    labels={"age": "Age", "chol": "Serum Cholesterol (mg/dl)"},
)

fig1.update_layout(template="plotly_white")
plotly(fig1)


# 2. Histogram of Age Distribution
text(
    """## Age Distribution \n
This histogram shows the age distribution of patients. 
The prevalence of heart disease increases noticeably in patients over 45."""
)
fig2 = px.histogram(
    df,
    x="age",
    color="diagnosis",
    title="Age Distribution",
    barmode="overlay",
    opacity=0.7
)
fig2.update_layout(template="plotly_white")
plotly(fig2)

# 3. Box plot - Resting Blood Pressure
text(
    """## Blood Pressure Comparison \n
This box plot compares resting blood pressure (trestbps) between groups. 
Patients with heart disease show slightly higher median blood pressure values."""
)
fig3 = px.box(
    df,
    x="diagnosis",
    y="trestbps",
    color="diagnosis",
    title="Resting Blood Pressure Distribution"
)
fig3.update_layout(template="plotly_white")
plotly(fig3)

# 4. Violin plot - Maximum Heart Rate
text(
    """## Maximum Heart Rate Distribution \n
The violin plot reveals patients with heart disease generally achieve lower maximum heart rates (thalach) during exercise, 
suggesting reduced cardiovascular capacity."""
)
fig4 = px.violin(
    df,
    x="diagnosis",
    y="thalach",
    color="diagnosis",
    title="Maximum Heart Rate Achieved"
)
fig4.update_layout(template="plotly_white")
plotly(fig4)


# Show data sample
text("## Dataset Preview \n First 10 rows of the heart disease dataset:")

# Convert '?' to NaN and drop rows with missing critical values
df.replace('?', pd.NA , inplace=True)

table(df, limit=10)



