from preswald import connect, text, table, slider, plotly
import pandas as pd
import plotly.express as px

# Connect to Preswald
connect()

try:
    df = pd.read_csv("data/mental_health.csv")
    df = df.head(200)  # Limit rows for performance
    text("Dataset loaded successfully!")
except Exception as e:
    text(f"ERROR: Failed to load dataset: {str(e)}")
    df = None

if df is None or df.empty:
    text("ERROR: Dataset not loaded. Ensure 'mental_health.csv' is inside 'data/' and properly configured.")
else:
    text("# Mental Health Care Trends in the U.S.")

    # Show first 20 rows
    table(df.head(20), title="Preview of Dataset (First 20 Rows)")


    threshold = slider("Minimum % Receiving Care", min_val=0, max_val=100, default=10)
    
    # Filter dataset
    filtered_df = df[df["Value"] >= threshold]

    # Remove "United States" from states
    filtered_df = filtered_df[filtered_df["State"] != "United States"]

    # Display filtered data (Limited to 20 rows)
    table(filtered_df.head(20), title=f"Filtered Data (≥ {threshold}% Receiving Care)")

    # Group by state and calculate the average value per state
    grouped_df = filtered_df.groupby("State", as_index=False)["Value"].mean()

    # Sort states by percentage receiving care
    sorted_df = grouped_df.sort_values(by="Value", ascending=False)

    # Show only the top 15 states for clarity
    top_states = sorted_df.head(15)

    fig = px.bar(
        top_states,
        x="Value",
        y="State",
        orientation="h",  # Horizontal bars for readability
        title="Top 15 States: Mental Health Care Trends",
        labels={"Value": "% Receiving Care", "State": "State"},
    )

    # Increase figure size & add margins for spacing
    fig.update_layout(
        height=800, 
        width=1000, 
        margin=dict(l=150, r=50, t=50, b=50), 
        yaxis=dict(tickmode="linear"), 
    )

    # Show visualization
    plotly(fig)
