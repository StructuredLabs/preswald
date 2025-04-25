from preswald import connect, get_df, table, text, slider, plotly
import plotly.express as px
import pandas as pd

# Step 1: Connect to the data source
connect()

# Step 2: Load the dataset
df = get_df("weather")

# Step 3: Check if the dataset loaded properly
if df is None or df.empty:
    text("Error: Dataset not found or not loaded correctly.")
else:
    # Convert the 'Date' column to datetime to avoid format issues
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Step 4: Display a title
    text("# Weather Data Analysis App")

    # Step 5: Add a temperature threshold slider
    threshold = slider("Temperature Threshold (°C)", min_val=15, max_val=30, default=20)

    # Step 6: Filter the dataset based on the temperature threshold
    filtered_df = df[df["Temperature (°C)"] > threshold]

    # Step 7: Display the filtered data
    if filtered_df.empty:
        text("No data matches the selected criteria.")
    else:
        table(filtered_df, title="Filtered Weather Data")

        # Step 8: Create a scatter plot with correct column names
        fig = px.scatter(filtered_df, x="Date", y="Temperature (°C)", color="Condition",
                         title="Temperature Over Time", labels={"Temperature (°C)": "Temperature (°C)"})

        # Step 9: Display the plot
        plotly(fig)
