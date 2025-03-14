import pandas as pd
import plotly.express as px
from preswald import connect, get_df, plotly, text

# Display the dashboard title
text("# Ice Cream Sales Analytics Dashboard 🍦")

# Connect to the data (if required by preswald)
connect()

# Load the data from the TOML-defined CSV file
data = get_df("ice_data")  # Use the name defined in the TOML file under [data.ice_data]

# Ensure numeric columns are properly formatted
data["Temperature (F)"] = pd.to_numeric(data["Temperature (F)"], errors="coerce")
data["Ice-cream Price ($)"] = pd.to_numeric(data["Ice-cream Price ($)"], errors="coerce")
data["Number of Tourists (thousands)"] = pd.to_numeric(data["Number of Tourists (thousands)"], errors="coerce")
data["Ice Cream Sales ($,thousands)"] = pd.to_numeric(data["Ice Cream Sales ($,thousands)"], errors="coerce")

# Add a new subsection for Ice Cream Sales Analysis
text("## Ice Cream Sales Analysis")

# Scatter Plot: Temperature vs. Ice Cream Sales
text("### Temperature vs. Ice Cream Sales")
fig_scatter = px.scatter(
    data,
    x="Temperature (F)",
    y="Ice Cream Sales ($,thousands)",
    color="Did it rain on that day?",
    title="Temperature vs. Ice Cream Sales",
    labels={
        "Temperature (F)": "Temperature (°F)",
        "Ice Cream Sales ($,thousands)": "Ice Cream Sales ($, thousands)",
    },
    hover_data=["Ice-cream Price ($)", "Number of Tourists (thousands)"],
)

# Update marker properties for better visibility
fig_scatter.update_traces(
    marker={
        "size": 10,  # Increase marker size
        "opacity": 0.8,  # Slightly transparent
    }
)

# Display the Scatter Plot
plotly(fig_scatter)

# Bar Chart: Ice Cream Sales by Rain Condition
text("### Ice Cream Sales by Rain Condition")
fig_bar = px.bar(
    data,
    x="Did it rain on that day?",
    y="Ice Cream Sales ($,thousands)",
    color="Did it rain on that day?",
    title="Ice Cream Sales by Rain Condition",
    labels={
        "Did it rain on that day?": "Rain Condition",
        "Ice Cream Sales ($,thousands)": "Ice Cream Sales ($, thousands)",
    },
)

# Scale down the bar chart
fig_bar.update_layout(
    xaxis_tickangle=0,  # Rotate x-axis labels for better readability
    height=400,  # Scale down the figure height
    title_x=0.5,  # Center the title
)

# Display the Bar Chart
plotly(fig_bar)

# Line Chart: Ice Cream Sales Over Time (Assuming a time column exists)
# Since the sample data doesn't have a time column, we'll create a dummy one for demonstration
data["Day"] = range(1, len(data) + 1)  # Add a dummy "Day" column

text("### Ice Cream Sales Over Time")
fig_line = px.line(
    data,
    x="Day",
    y="Ice Cream Sales ($,thousands)",
    title="Ice Cream Sales Over Time",
    labels={
        "Day": "Day",
        "Ice Cream Sales ($,thousands)": "Ice Cream Sales ($, thousands)",
    },
    markers=True,
)

# Enhance line and marker visibility
fig_line.update_traces(
    line={"width": 3}, marker={"size": 8}
)
fig_line.update_layout(
    xaxis_title="Day",
    yaxis_title="Ice Cream Sales ($, thousands)",
    xaxis_tickangle=0,  # Rotate x-axis labels for readability
    height=400,  # Adjust the height for a cleaner display
)

# Display the Line Chart
plotly(fig_line)