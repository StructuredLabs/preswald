from preswald import text, plotly, connect,query,table
from preswald.interfaces.components import slider
from preswald.interfaces.data import get_df 
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df("sample_csv")

sql = "SELECT * FROM sample_csv;"
filtered_df = query(sql, "sample_csv")

# print(len(filtered_df))

text("# Iris Dataset Analysis")
text("## Visualization of data across all petal_length (cm)")

if df is not None:
    # Filter the dataset dynamically based on the slider value
    # print(df["PetalLengthCm"])
    petal_threshold = slider("Petal Length Threshold", min_val=1.0, max_val=6.9, default=3.5)
    dynamic_filtered_df = df[df["PetalLengthCm"] > petal_threshold]
    table(dynamic_filtered_df, title="Dynamic Iris Data View")

    # Create a scatter plot for sepal dimensions, colored by species
    fig = px.scatter(
    dynamic_filtered_df,
    x="SepalLengthCm",
    y="SepalWidthCm",
    color="Species",  # Different colors for each species
    title="Sepal Dimensions by Species (Dynamic Filter)",
)

    # Label axes
    fig.update_layout(
    title="Sepal Length (x) vs Sepal Width (y) by Species (Dynamic Filter)",  # Main title
    xaxis=dict(title="Sepal Length (cm)"),  # X-axis title
    yaxis=dict(title="Sepal Width (cm)"),   # Y-axis title
    template="plotly_white" 
    )

    # Remove fixed light blue color, allowing species-based coloring
    fig.update_traces(textposition="top center", marker=dict(size=10))
    plotly(fig)
else:
    text("Cannot display visualizations because the dataset 'Iris.csv' could not be loaded.")


# # Display the query result table
# table(filtered_df, title="Filtered Iris Data")
# petal_threshold = slider("Petal Length Threshold", min_val=1.0, max_val=7.0, default=3.0)

# dynamic_filtered_df = df[df["petal_length"] > petal_threshold]
# table(dynamic_filtered_df, title="Dynamic Iris Data View")


# # Create a scatter plot
# fig = px.scatter(
#     dynamic_filtered_df,
#     x="sepal_length",
#     y="sepal_width",
#     color="species",
#     title="Sepal Dimensions by Species (Dynamic Filter)"
# )

# # Add labels for each point
# fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# # Style the plot
# fig.update_layout(template='plotly_white')

# # Show the plot
# plotly(fig)

# Show the data
# table(df)
