from preswald import connect, get_df, table, text, slider, plotly
import pandas as pd
import plotly.express as px

# 🟢 Display a title
text("# 📊 My Data Analysis App")

# 🟢 Step 1: Connect to Preswald
try:
    connect()
    text("✅ Connection to Preswald initialized successfully!")
except Exception as e:
    text(f"🚨 Error initializing connection: {e}")
    exit()

# 🟢 Step 2: Load the dataset
try:
    df = get_df("sample")  # Ensure "sample" matches `preswald.toml`
    if df is None:
        raise ValueError("Dataset returned None")

    text(f"✅ Dataset Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print("Dataset columns:", df.columns.tolist())  # Debugging

except Exception as e:
    text("🚨 Error: Dataset could not be loaded!")
    text(f"Details: {e}")
    print("🚨 ERROR: Dataset failed to load:", e)
    df = None

# 🟢 Step 3: UI Component - Add a slider
text("📌 Adjust the slider below to filter data.")
threshold = slider("Filter Threshold", min_val=0, max_val=100, default=50)

# 🟢 Step 4: Ensure the dataset has required columns
if df is not None and "value" in df.columns:
    # Filter data based on slider
    filtered_df = df[df["value"] > threshold]
    table(filtered_df, title="🔍 Filtered Data")

    # Generate a scatter plot (ensure required columns exist)
    if "quantity" in df.columns:
        fig = px.scatter(df, x="quantity", y="value", color="item", title="🔍 Quantity vs. Value")
        plotly(fig)
    else:
        text("🚨 Error: Column 'quantity' not found!")

else:
    text("🚨 Error: Required column 'value' is missing! Dataset might be incorrect.")

