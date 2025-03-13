import plotly.express as px
from preswald import connect, get_df, plotly, table, text

# Report Title
text(
    "# Diabetes Data Visualization \n This report provides a visual analysis of the diabetes dataset, exploring key health indicators and their relationships."
)

# Load the CSV
df = get_df("diabetes_csv")

# 1. Scatter plot - Glucose vs BMI
text(
    "## Glucose vs BMI \n This scatter plot shows the relationship between glucose levels and BMI. Higher glucose levels may be associated with higher BMI values."
)
fig1 = px.scatter(
    df,
    x="Glucose",
    y="BMI",
    color="Outcome",
    title="Glucose vs BMI",
    labels={"Glucose": "Glucose Level", "BMI": "Body Mass Index"},
)
fig1.update_layout(template="plotly_white")
plotly(fig1)

# 2. Histogram of Glucose Levels
text(
    "## Distribution of Glucose Levels \n This histogram displays the distribution of glucose levels in the dataset."
)
fig2 = px.histogram(
    df, x="Glucose", color="Outcome", title="Distribution of Glucose Levels"
)
fig2.update_layout(template="plotly_white")
plotly(fig2)

# 3. Box plot of BMI by Outcome
text(
    "## BMI Distribution by Outcome \n This box plot shows the spread of BMI values for diabetic and non-diabetic individuals."
)
fig3 = px.box(
    df, x="Outcome", y="BMI", color="Outcome", title="BMI Distribution by Outcome"
)
fig3.update_layout(template="plotly_white")
plotly(fig3)

# 4. Violin plot of Age by Outcome
text(
    "## Age Distribution by Outcome \n The violin plot provides a better understanding of the distribution of age within each outcome category."
)
fig4 = px.violin(
    df, x="Outcome", y="Age", color="Outcome", title="Age Distribution by Outcome"
)
fig4.update_layout(template="plotly_white")
plotly(fig4)

# 5. Density contour plot - Glucose vs Insulin
text(
    "## Density Contour: Glucose vs Insulin \n This density contour plot illustrates the relationship between glucose and insulin levels, highlighting concentration areas."
)
fig5 = px.density_contour(
    df, x="Glucose", y="Insulin", color="Outcome", title="Density Contour of Glucose vs Insulin"
)
fig5.update_layout(template="plotly_white")
plotly(fig5)

# Show the first 10 rows of the dataset
text(
    "## Sample of the Diabetes Dataset \n Below is a preview of the first 10 rows of the dataset, showing key health measurements."
)
table(df, limit=10)
