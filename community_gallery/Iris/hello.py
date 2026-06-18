from preswald import text, connect, query, slider, view, plotly
import pandas as pd
import plotly.express as px
#import plotly.express as px

"""text("# Welcome to Preswald!")
text("This is your first app. 🎉")"""

# Load dataset manually
df = pd.read_csv("E:\Preswald\my_example_project\data\Iris.csv")  # Update with your actual file name
df = pd.DataFrame(df) 
# Query data (modify as needed)
#df = query("SELECT * FROM my_dataset")
# Title
text("# My Data Analysis App")

text("### Dataset Preview")
text(str(df.head()))

# Add a slider for filtering (Modify column name)
column_name = "SepalLengthCm"
if column_name in df.columns:
    # Add a slider for filtering
    threshold = slider("Threshold", min_val=float(df[column_name].min()), max_val=float(df[column_name].max()), default=float(df[column_name].median()))
    # Extract value if needed
    if isinstance(threshold, dict):
        threshold = threshold.get("value", df[column_name].median())

    # Filtered Data
    filtered_df = df[df[column_name] > threshold]
    text("### Filtered Data")
    text(str(filtered_df.head()))
else:
    text("Error: Column name not found in dataset")
# Filtered Data
#filtered_df = df[df[column_name] > threshold]
fig = px.scatter(df, x="SepalLengthCm", y="SepalWidthCm", color="Species")
plotly(fig)
#prswld-40e091ae-8270-4064-b854-43060da688b5