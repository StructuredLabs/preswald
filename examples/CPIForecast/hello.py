from preswald import text, plotly, table, slider
import pandas as pd
import plotly.express as px

# Load the dataset using pandas
csv_path = "data/CPIForecast.csv"  # Ensure this path is correct
df = pd.read_csv(csv_path)

# Rename columns properly (Check actual column names from Step 2)
df.columns = ["Category", "Subcategory", "Other", "Col4", "Col5", "Year", "Metric", "Value"]

# Convert "Value" to numeric and rename it to "Percent_Change"
df["Value"] = pd.to_numeric(df["Value"], errors="coerce")  # Convert to float
df = df.rename(columns={"Value": "Percent_Change"})

# Remove NaN values
df = df.dropna(subset=["Percent_Change"])

# Display table
table(df.head(), title="Sample Data")

# Add a slider for filtering
threshold = slider("Threshold", min_val=-5, max_val=15, default=0)
filtered_df = df[df["Percent_Change"] > threshold]
table(filtered_df, title="Filtered Data")

# Create a scatter plot
fig = px.scatter(df, x="Year", y="Percent_Change", title="Food Price Percent Changes Over Time")
plotly(fig)
