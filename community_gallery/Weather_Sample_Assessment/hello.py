from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px

# **Step 1: Load the dataset**
text("# Welcome to the Weather Data App!")
connect()  # Initialize connection to preswald.toml data sources
df = get_df("weather_csv")  # Load weather dataset

if df is None:
    text("Dataset 'weather_csv' could not be loaded.")
else:
    text("Weather dataset loaded successfully!")

# **Step 2: Query or manipulate the data**
sql = "SELECT * FROM weather_csv WHERE MaxTemp > 25"  # Example SQL query filtering max temp > 25
filtered_df = query(sql, "weather_csv")

# **Step 3: Build an interactive UI**
text("## Filtered Weather Data (Max Temp > 25°C)")
table(filtered_df, title="Filtered Weather Data")

# Add user controls: Slider for dynamic filtering by MaxTemp
text("### Adjust the temperature threshold dynamically:")
threshold = slider("Temperature Threshold (°C)", min_val=10, max_val=40, default=25)

# Dynamic filtering based on slider input
dynamic_filtered_df = df[df["MaxTemp"] > threshold]
table(dynamic_filtered_df, title=f"Weather Data (MaxTemp > {threshold}°C)")

# **Step 4: Create a visualization**
text("## Temperature vs. Rainfall Scatter Plot")
fig = px.scatter(df, x="MaxTemp", y="Rainfall", color="RainTomorrow",
                 title="Max Temperature vs Rainfall",
                 labels={"MaxTemp": "Max Temperature (°C)", "Rainfall": "Rainfall (mm)"},
                 size_max=10)

plotly(fig)  # Display the plot

# Rainfall Distribution (Histogram)
text("## Rainfall Distribution")
fig = px.histogram(df, x="Rainfall", nbins=30, color="RainTomorrow", 
                   title="Rainfall Distribution",
                   labels={"Rainfall": "Rainfall (mm)"},
                   color_discrete_map={"Yes": "blue", "No": "orange"})
plotly(fig)