from preswald import connect, get_df, table, text, slider, plotly
import plotly.express as px

# Initialize connection
connect()

# Load the dataset
df = get_df("sample")
print(df)

# Debugging step: Print df to check if it's loading
text(f"Dataset Loaded: {df}")

# If df is None, stop execution
if df is None:
    text("Error: Dataset not found. Please check your data path.")
else:
    # Display a title
    text("# Inventory Data Analysis App")

    # Create a filter using a slider for minimum value
    threshold = slider("Minimum Value", min_val=0, max_val=200, default=50)

    # Filter dataset based on value
    filtered_df = df[df["value"] > threshold]

    # Show filtered data
    table(filtered_df, title="Filtered Inventory Data")

    # Create a bar chart for item values
    fig = px.bar(df, x="item", y="value", color="quantity", title="Item Values in Inventory")
    plotly(fig)
