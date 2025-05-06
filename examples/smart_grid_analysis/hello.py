from preswald import text, plotly, connect, get_df, selectbox, checkbox, table
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

text("# ⚡ Smart Grid Load Monitoring Dashboard")
text("""
This dashboard provides monitoring and analysis of our smart grid infrastructure, helping operators and analysts to:
- Track power quality metrics and grid stability 
- Monitor renewable energy integration
- Analyze environmental impacts on power consumption
- Identify potential issues before they become critical
- Make data-driven decisions for grid optimization
""")

connect()
df = get_df("smart_grid_dataset")
df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
df.sort_values(by="Timestamp", inplace=True)

text("## Analysis Period Selection")

# Get current date
current_date = datetime.now()

# Extract unique years, months, and days and convert to regular Python integers
unique_years = sorted([int(year) for year in df["Timestamp"].dt.year.unique()])
selected_year = selectbox("Select Year", 
    options=[str(year) for year in unique_years],
    default=str(current_date.year)
)
selected_year = int(selected_year)

# Filter months based on selected year
available_months = sorted(df[df["Timestamp"].dt.year == selected_year]["Timestamp"].dt.month.unique())

# Check if there are any available months
if len(available_months) == 0:
    text(f"No data available for year {selected_year}")
    month_options = ["1"]  # Default to January
    selected_month = 1
else:
    month_options = [str(m) for m in available_months]
    # If current year, only show months up to current month
    if selected_year == current_date.year:
        month_options = [m for m in month_options if int(m) <= current_date.month]
    selected_month = selectbox("Select Month", 
        options=month_options,
        default=month_options[0]
    )
    selected_month = int(selected_month)

# Filter days based on selected year and month
available_days = sorted(df[
    (df["Timestamp"].dt.year == selected_year) & 
    (df["Timestamp"].dt.month == selected_month)
]["Timestamp"].dt.day.unique())

# Check if there are any available days
if len(available_days) == 0:
    text(f"No data available for {selected_year}-{selected_month}")
    day_options = ["1"]  # Default to day 1
    selected_day = 1
else:
    day_options = [str(d) for d in available_days]
    # If current year and month, only show days up to current day
    if selected_year == current_date.year and selected_month == current_date.month:
        day_options = [d for d in day_options if int(d) <= current_date.day]
    selected_day = selectbox("Select Day", 
        options=day_options,
        default=day_options[0]
    )
    selected_day = int(selected_day)

# Add granularity selection
granularity = selectbox("Select Time Granularity",
    options=["Year", "Month", "Day"],
    default="Month"
)

# Filter data based on selection and granularity
if granularity == "Year":
    filtered_df = df[df["Timestamp"].dt.year == selected_year].copy()
elif granularity == "Month":
    filtered_df = df[
        (df["Timestamp"].dt.year == selected_year) & 
        (df["Timestamp"].dt.month == selected_month)
    ].copy()
else:  # Day
    filtered_df = df[
        (df["Timestamp"].dt.year == selected_year) & 
        (df["Timestamp"].dt.month == selected_month) &
        (df["Timestamp"].dt.day == selected_day)
    ].copy()

# Add warning if no data is available
if len(filtered_df) == 0:
    text("⚠️ No data available for the selected time period")

# Add date range info
if len(filtered_df) > 0:
    text(f"Showing data for: {filtered_df['Timestamp'].min().strftime('%Y-%m-%d')} to {filtered_df['Timestamp'].max().strftime('%Y-%m-%d')}")
else:
    text("No data available for selected period")

# Convert timestamps for plotting
filtered_df_plot = filtered_df.copy()
filtered_df_plot["Timestamp"] = filtered_df_plot["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

text("## Grid Performance Overview")

text("### 1. Power Quality Metrics (Dual-Axis Line Chart)")
text("""
Purpose: Monitors grid stability and efficiency
- High voltage variations could indicate grid issues
- Power Factor shows how efficiently power is being used (closer to 1.0 is better)
""")

show_voltage = checkbox("Voltage", default=True, size=0.1)
show_power_factor = checkbox("Power Factor", default=True, size=0.5)


# Modify the Power Quality Metrics graph
quality_fig = make_subplots(specs=[[{"secondary_y": True}]])
quality_fig.add_trace(
    go.Scatter(
        x=filtered_df_plot["Timestamp"],
        y=filtered_df["Voltage (V)"],
        name="Voltage",
        line=dict(color='blue'),
        hovertemplate="Voltage: %{y:.2f}V<br>Time: %{x}",
        visible=show_voltage
    ),
    secondary_y=False
)
quality_fig.add_trace(
    go.Scatter(
        x=filtered_df_plot["Timestamp"],
        y=filtered_df["Power Factor"],
        name="Power Factor",
        line=dict(color='red'),
        hovertemplate="PF: %{y:.2f}<br>Time: %{x}",
        visible=show_power_factor
    ),
    secondary_y=True
)
quality_fig.update_layout(
    title_text="Power Quality Metrics",
    hovermode="x unified",
    margin=dict(l=50, r=50, t=50, b=30),
    height=400,
    title_x=0.5
)
quality_fig.update_yaxes(title_text="Voltage (V)", secondary_y=False)
quality_fig.update_yaxes(title_text="Power Factor", secondary_y=True)
plotly(quality_fig)

text("### 2. Grid Supply Sources (Stacked Area Chart)")
text("""
Purpose: Shows the renewable vs traditional energy mix
- Stacked format helps see total power supply and relative contributions
- Useful for tracking renewable energy goals
""")

show_solar = checkbox("Solar", default=True, size=0.3)
show_wind = checkbox("Wind", default=True, size=0.3)
show_grid = checkbox("Grid", default=True, size=0.3)

# Modify the Grid Supply Sources graph
supply_fig = go.Figure()
for source, color, fillcolor in [
    ("Solar Power (kW)", "orange", "rgba(255,165,0,0.5)"),
    ("Wind Power (kW)", "green", "rgba(50,205,50,0.5)"),
    ("Grid Supply (kW)", "gray", "rgba(128,128,128,0.5)")
]:
    supply_fig.add_trace(
        go.Scatter(
            x=filtered_df_plot["Timestamp"],
            y=filtered_df[source],
            name=source.split()[0],
            fill='tonexty',
            fillcolor=fillcolor,
            line=dict(color=color),
            stackgroup='supply',
            hovertemplate=f"{source.split()[0]}: %{{y:.2f}}kW<br>Time: %{{x}}",
            visible=locals()[f"show_{source.split()[0].lower()}"]
        )
    )
supply_fig.update_layout(
    title_text="Grid Supply Sources",
    yaxis_title="Power (kW)",
    xaxis_title="Time",
    hovermode="x unified",
    margin=dict(l=50, r=50, t=50, b=30),
    height=400,
    title_x=0.5
)
plotly(supply_fig)

text("### 3. Environmental Impact Analysis (Scatter Plot)")
text("""
Shows relationship between:
- Temperature (x-axis)
- Power Consumption (y-axis)
- Humidity (color intensity)
Purpose: Understand how weather affects energy usage
- Helps predict demand based on weather forecasts
""")

env_fig = go.Figure()
env_fig.add_trace(
    go.Scatter(
        x=filtered_df["Temperature (°C)"],
        y=filtered_df["Power Consumption (kW)"],
        mode='markers',
        marker=dict(
            size=8,
            color=filtered_df["Humidity (%)"],
            colorbar=dict(title="Humidity (%)"),
            colorscale='Viridis',
            showscale=True
        ),
        name='Consumption vs Temp',
        hovertemplate="Power: %{y:.2f}kW<br>Temp: %{x}°C"
    )
)
env_fig.update_layout(
    margin=dict(l=50, r=50, t=50, b=30),
    height=400,
    title_x=0.5,
    showlegend=True,
    legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
)
plotly(env_fig)

text("### 4. Key Metrics Summary Table")
metrics = [
    ('Average Power Consumption (kW)', 'Power Consumption (kW)', 'mean'),
    ('Peak Power Consumption (kW)', 'Power Consumption (kW)', 'max'),
    ('Average Voltage (V)', 'Voltage (V)', 'mean'),
    ('Average Power Factor', 'Power Factor', 'mean'),
    ('Total Solar Generation (kWh)', 'Solar Power (kW)', 'sum'),
    ('Total Wind Generation (kWh)', 'Wind Power (kW)', 'sum')
]
summary_df = pd.DataFrame({
    'Metric': [m[0] for m in metrics],
    'Value': [f"{getattr(filtered_df[m[1]], m[2])():.2f}" for m in metrics]
})
table(summary_df)
