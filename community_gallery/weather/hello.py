import plotly.express as px

from preswald import connect, get_df, plotly, table, text


# Title and Introduction
text("# Temperature vs Humidity Analysis 🌡️💧")
text(
    "This project visualizes the relationship between temperature and humidity using a scatter plot. The dataset includes temperature (°C) and humidity (%) readings from various locations."
)

# Load the CSV
connect()  # Load in all sources, which by default includes 'sample_csv'
df = get_df("sample_csv")

# Data Overview
text("## Dataset Overview 📊")
text(f"- Number of Records: {len(df)}")
text("- Features: Temperature_C (°C), Humidity_pct (%)")
text("- Each point represents a recorded value from a specific location.")

# Create a scatter plot
fig = px.scatter(
    df,
    x="Temperature_C",
    y="Humidity_pct",
    text="Location",
    title="Temperature vs. Humidity",
    labels={"Temperature_C": "Temperature (°C)", "Humidity_pct": "Humidity (%)"},
)

# Add labels for each point
fig.update_traces(textposition="top center", marker=dict(size=12, color="lightblue"))

# Style the plot
fig.update_layout(template="plotly_white")

# Display the Plot
text("## Scatter Plot: Temperature vs. Humidity 📈")
text(
    "The scatter plot below shows how humidity varies with temperature. Locations are labeled for reference."
)
plotly(fig)

# Show the data
text("## Raw Data Table 📋")
table(df)
