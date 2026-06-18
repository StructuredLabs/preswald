from preswald import text, plotly, connect, get_df, table, query, slider
import plotly.express as px
import pandas as pd

# App Title
text("# Shark Tank Data Analysis App")

# 1️. Load the Dataset
connect()  
df = get_df("SharkTank")  # Ensure dataset name is correct

if df is None or df.empty:
    text("Error: Data could not be loaded! Check `preswald.toml` settings or dataset content.")
else:
    text("Dataset loaded successfully!")

    # Convert numerical columns to float
    for col in df.select_dtypes(include=['int64', 'float64']).columns:
        df[col] = df[col].astype(float)

    table(df.head(), title="Preview of Dataset")  

    # 2️. Query or Manipulate the Data
    sql = "SELECT * FROM SharkTank WHERE `Total Deal Amount` > 100000"  # Updated condition
    filtered_df = query(sql, "SharkTank")

    if filtered_df is None or filtered_df.empty:
        text("SQL query returned no results! Adjust the filter conditions.")
    else:
        text("SQL query executed successfully! Displaying filtered data:")
        table(filtered_df, title="Filtered Data")

    # 3️. Add User Controls
    threshold = slider("Threshold", min_val=0, max_val=df["Total Deal Amount"].max(), default=100000)
    filtered_dynamic_df = df[df["Total Deal Amount"] > threshold]

    text(f"Displaying Startups with Deals Greater than ${threshold:,}")
    table(filtered_dynamic_df, title="Dynamic Data View")

    # 4️. Create an Interactive Visualization
    if {"Original Ask Amount", "Total Deal Amount", "Startup Name"}.issubset(df.columns):
        fig = px.scatter(
            df, x="Original Ask Amount", y="Total Deal Amount", text="Startup Name",
            title="Original Ask vs. Total Deal Amount",
            labels={"Original Ask Amount": "Investment Requested ($)", "Total Deal Amount": "Investment Received ($)"}
        )
        fig.update_traces(textposition="top center", marker=dict(size=10, color='blue'))
        fig.update_layout(template='plotly_white')
        plotly(fig)
    else:
        text("Missing required columns for visualization!")
