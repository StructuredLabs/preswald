from preswald import connect, get_df, table, text, slider, plotly
import plotly.express as px
import pandas as pd

# Connect to Preswald and load dataset
connect()
df = get_df("sample_csv")

# Ensure 'mcg' column is numeric
df["mcg"] = pd.to_numeric(df["mcg"], errors="coerce")
df = df.dropna(subset=["mcg"])  # Remove rows with NaN in 'mcg'

# Debugging print (remove later if needed)
print("Min mcg:", df["mcg"].min(), "Max mcg:", df["mcg"].max(), "Median mcg:", df["mcg"].median())

# Page Title
text("# 🍞 Yeast Data Analysis 🦠")
text("### Explore and analyze yeast dataset interactively.")

# Display Full Dataset
table(df, title="Complete Yeast Dataset")

# Interactive Filtering
if not df.empty:  # Ensure df has data before setting the slider
    threshold = slider(
        "Filter by mcg value",
        min_val=float(df["mcg"].min()),
        max_val=float(df["mcg"].max()),
        default=float(df["mcg"].median())
    )
    filtered_df = df[df["mcg"] > threshold]
    table(filtered_df, title=f"Filtered Yeast Data (mcg > {threshold})")

# Scatter Plot Visualization
if "mcg" in df.columns and "gvh" in df.columns:
    fig = px.scatter(df, x="mcg", y="gvh", color="name", title="Yeast Feature Correlation", template="plotly_dark")
    plotly(fig)
