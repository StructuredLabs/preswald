from preswald import connect, get_df, slider, table, text
from preswald.engine.runner import validate_dataframe_operation


text("# DataFrame Validation Example")

# Initialize connection
connect()

# Load sample data
df = get_df("weatherhistory_csv")

# Show available columns
text("## Available Columns")
text(f"Columns in the dataset: {', '.join(df.columns)}")

# Example 1: Valid column access
text("## Example 1: Valid Column Access")
threshold = slider("Humidity Threshold", min_val=0, max_val=1, default=0.5)
# Use validation function before operation
validate_dataframe_operation(df, "Humidity", "filtering")
table(df[df["Humidity"] > threshold], title="Filtered by Humidity")

# Example 2: Invalid column access (will show helpful error)
text("## Example 2: Invalid Column Access")
threshold2 = slider("Value Threshold", min_val=0, max_val=100, default=50)
try:
    validate_dataframe_operation(df, "value", "filtering")
    table(df[df["value"] > threshold2], title="Filtered by Value")
except ValueError as e:
    text(f"Error: {e!s}")
