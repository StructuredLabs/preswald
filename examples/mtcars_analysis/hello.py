from preswald import connect, text, table, slider, plotly
import pandas as pd
import plotly.express as px

# Load data directly with pandas
df = pd.read_csv("data/mtcars.csv")

# Create the UI
text("# Car Performance Analysis App")
text("## Dataset Overview")
table(df.head(10), title="Motor Trend Car Road Tests")

# Add interactive controls
text("## Interactive Filtering")
mpg_threshold = slider("MPG Threshold", min_val=10, max_val=35, default=20)
filtered_df = df[df["mpg"] > mpg_threshold]
table(filtered_df, title=f"Cars with MPG > {mpg_threshold}")

# Show some statistics
text("## Data Analysis")
cylinders = sorted(df["cyl"].unique())
for cyl in cylinders:
    subset = df[df["cyl"] == cyl]
    text(f"### {cyl} Cylinder Cars")
    text(f"Average MPG: {subset['mpg'].mean():.2f}")
    text(f"Average Horsepower: {subset['hp'].mean():.2f}")
    table(subset, title=f"Cars with {cyl} cylinders")

# Create a visualization
text("## Visualizations")
fig1 = px.scatter(df, x="mpg", y="hp", color="cyl", 
                 size="wt", hover_name="model",
                 title="MPG vs Horsepower by Cylinder Count")
plotly(fig1)

# Relationship between weight and MPG (without OLS trendline)
fig2 = px.scatter(df, x="wt", y="mpg",
                 title="Relationship Between Weight and MPG")
fig2.update_layout(xaxis_title="Weight (1000 lbs)", yaxis_title="Miles Per Gallon")
plotly(fig2)

# bar chart visualization
text("## Average MPG by Cylinder Count")
avg_mpg_by_cyl = df.groupby("cyl")["mpg"].mean().reset_index()
fig3 = px.bar(avg_mpg_by_cyl, x="cyl", y="mpg", 
             title="Average MPG by Number of Cylinders")
fig3.update_layout(xaxis_title="Number of Cylinders", yaxis_title="Average MPG")
plotly(fig3)