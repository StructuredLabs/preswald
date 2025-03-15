import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from preswald import connect, get_df, plotly, table, text, selectbox, slider, checkbox, text_input
import datetime

text("# 🚗 Uber Ridesharing Analysis \nInteractive analysis of NYC Uber trip data from January-February 2015")

# Load the Uber data
connect()  # load in all sources
uber_df = get_df('uber_csv')

# Convert date column to datetime
uber_df['date'] = pd.to_datetime(uber_df['date'])

# Add useful derived columns
uber_df['trips_per_vehicle'] = uber_df['trips'] / uber_df['active_vehicles']
uber_df['day_of_week'] = uber_df['date'].dt.day_name()
uber_df['weekday'] = uber_df['date'].dt.dayofweek
uber_df['is_weekend'] = uber_df['weekday'] >= 5
uber_df['day_type'] = uber_df['is_weekend'].map({True: 'Weekend', False: 'Weekday'})
uber_df['month'] = uber_df['date'].dt.month_name()
uber_df['day_num'] = uber_df['date'].dt.day
uber_df['date_str'] = uber_df['date'].dt.strftime('%Y-%m-%d')
uber_df['week_of_year'] = uber_df['date'].dt.isocalendar().week

# Create filter options - combine header and description
text("## 🔍 Data Filters\nAdjust the filters below to explore different aspects of the Uber data")

# Base selection filter
all_bases = uber_df['dispatching_base_number'].unique().tolist()
all_bases.insert(0, "All Bases")
selected_base = selectbox("Select a base to analyze:", all_bases)

# Date range filter - use numeric approach
start_date = uber_df['date'].min().date()
end_date = uber_df['date'].max().date()
date_range = (end_date - start_date).days  # Total days in our dataset

# Create slider with day offsets (0 to number of days in range)
day_offset = slider(
    "Select date (drag to adjust):",
    min_val=0,
    max_val=date_range,
    default=0
)

# Calculate selected date by adding offset to start date
selected_date = start_date + datetime.timedelta(days=int(day_offset))
text(f"Showing data from: **{selected_date.strftime('%B %d, %Y')}** onwards")

# Apply filters
filtered_df = uber_df.copy()
if selected_base != "All Bases":
    filtered_df = filtered_df[filtered_df['dispatching_base_number'] == selected_base]

# Filter by date - handling the case where selected_date is a single date
filtered_df = filtered_df[filtered_df['date'].dt.date >= selected_date]

# Display summary statistics
text("## 📊 Key Metrics Overview")
total_trips = filtered_df['trips'].sum()
total_active_vehicles = filtered_df['active_vehicles'].sum()
avg_trips_per_vehicle = total_trips / total_active_vehicles if total_active_vehicles > 0 else 0
date_min = filtered_df['date'].min().strftime('%B %d, %Y')
date_max = filtered_df['date'].max().strftime('%B %d, %Y')

summary_df = pd.DataFrame({
    'Metric': ['Total Trips', 'Total Active Vehicles', 'Avg Trips per Vehicle', 'Date Range'],
    'Value': [f"{total_trips:,}", f"{total_active_vehicles:,}", 
              f"{avg_trips_per_vehicle:.2f}", f"{date_min} to {date_max}"]
})

table(summary_df)

# Time series analysis - combine header and description
text("## 📈 Trip Volume Trends\nAnalyze how trip volume changes over time")

show_moving_avg = checkbox("Show 7-day moving average", default=True)

# Group by date and convert date to string for plotting
daily_trips = filtered_df.groupby('date').agg({
    'trips': 'sum',
    'active_vehicles': 'sum'
}).reset_index()
daily_trips['date_str'] = daily_trips['date'].dt.strftime('%Y-%m-%d')

# Add moving average if selected
if show_moving_avg and len(daily_trips) > 7:
    daily_trips['7_day_avg_trips'] = daily_trips['trips'].rolling(window=7).mean()

# Create time series visualization
metric_options = ["trips", "active_vehicles", "trips_per_vehicle"]
selected_metric = selectbox("Select metric to visualize:", metric_options, default="trips")

if selected_metric == "trips_per_vehicle":
    daily_trips['trips_per_vehicle'] = daily_trips['trips'] / daily_trips['active_vehicles']
    y_column = 'trips_per_vehicle'
    y_label = 'Trips per Vehicle'
else:
    y_column = selected_metric
    y_label = 'Trips' if selected_metric == 'trips' else 'Active Vehicles'

fig_time = px.line(
    daily_trips,
    x='date_str',
    y=y_column,
    title=f'Daily {y_label} Over Time',
    labels={y_column: y_label, 'date_str': 'Date'},
)

# Add moving average line if selected
if show_moving_avg and '7_day_avg_trips' in daily_trips.columns and selected_metric == 'trips':
    fig_time.add_scatter(
        x=daily_trips['date_str'], 
        y=daily_trips['7_day_avg_trips'],
        mode='lines',
        name='7-day Moving Average',
        line=dict(width=2, dash='dash', color='red')
    )

fig_time.update_layout(template='plotly_white', hovermode='x unified')
plotly(fig_time)

# Day of week performance analysis - combine header and description
text("## 📆 Day of Week Patterns\nDiscover which days of the week have the highest activity")

# Group by day of week
day_perf = filtered_df.groupby('day_of_week').agg({
    'trips': 'sum',
    'active_vehicles': 'sum',
    'date': 'nunique'  # Count unique dates to normalize
}).reset_index()

# Calculate metrics
day_perf['avg_daily_trips'] = day_perf['trips'] / day_perf['date']
day_perf['avg_daily_vehicles'] = day_perf['active_vehicles'] / day_perf['date']
day_perf['avg_trips_per_vehicle'] = day_perf['avg_daily_trips'] / day_perf['avg_daily_vehicles']

# Create ordered day categories
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_perf['day_of_week'] = pd.Categorical(day_perf['day_of_week'], categories=day_order, ordered=True)
day_perf = day_perf.sort_values('day_of_week')

# Create visualization
day_metric = selectbox(
    "Select day of week metric:", 
    ["Average Daily Trips", "Average Trips per Vehicle"],
    default="Average Daily Trips"
)

if day_metric == "Average Daily Trips":
    fig_day = px.bar(
        day_perf,
        x='day_of_week',
        y='avg_daily_trips',
        title='Average Daily Trips by Day of Week',
        labels={'avg_daily_trips': 'Avg Trips', 'day_of_week': 'Day'},
        color='avg_daily_trips',
        color_continuous_scale='Viridis',
        text_auto='.0f'
    )
else:
    fig_day = px.bar(
        day_perf,
        x='day_of_week',
        y='avg_trips_per_vehicle',
        title='Average Trips per Vehicle by Day of Week',
        labels={'avg_trips_per_vehicle': 'Avg Trips per Vehicle', 'day_of_week': 'Day'},
        color='avg_trips_per_vehicle',
        color_continuous_scale='Viridis',
        text_auto='.1f'
    )

fig_day.update_layout(template='plotly_white')
plotly(fig_day)

# Weekly growth analysis - combine header and description
text("## 📊 Growth Analysis\nExamine week-over-week growth rates to identify trends")

# Calculate week-over-week metrics
weekly_data = filtered_df.groupby('week_of_year').agg({
    'trips': 'sum',
    'active_vehicles': 'sum',
    'date': 'nunique'  # Number of days with data in each week
}).reset_index()

# Calculate daily averages to normalize weeks with partial data
weekly_data['avg_daily_trips'] = weekly_data['trips'] / weekly_data['date']
weekly_data['avg_daily_vehicles'] = weekly_data['active_vehicles'] / weekly_data['date']

# Add week-over-week growth rate
if len(weekly_data) > 1:
    weekly_data['trips_growth'] = weekly_data['avg_daily_trips'].pct_change() * 100
    weekly_data['vehicles_growth'] = weekly_data['avg_daily_vehicles'].pct_change() * 100
    weekly_data['week_label'] = 'Week ' + weekly_data['week_of_year'].astype(str)
    
    # Plot weekly growth
    growth_metrics = selectbox(
        "Select growth metric to view:", 
        ["Trip Growth (%)", "Vehicle Growth (%)", "Both"],
        default="Trip Growth (%)"
    )
    
    if growth_metrics in ["Trip Growth (%)", "Both"]:
        fig_growth = px.bar(
            weekly_data.iloc[1:],  # Skip first week (no growth rate)
            x='week_label',
            y='trips_growth',
            title='Week-over-Week Trip Growth',
            labels={'trips_growth': 'Growth Rate (%)', 'week_label': 'Week'},
            color='trips_growth',
            color_continuous_scale='RdYlGn',  # Red for negative, green for positive
            text_auto='.1f'
        )
        fig_growth.update_layout(template='plotly_white')
        plotly(fig_growth)
    
    if growth_metrics in ["Vehicle Growth (%)", "Both"]:
        fig_vehicle_growth = px.bar(
            weekly_data.iloc[1:],  # Skip first week (no growth rate)
            x='week_label',
            y='vehicles_growth',
            title='Week-over-Week Vehicle Growth',
            labels={'vehicles_growth': 'Growth Rate (%)', 'week_label': 'Week'},
            color='vehicles_growth',
            color_continuous_scale='RdYlGn',  # Red for negative, green for positive
            text_auto='.1f'
        )
        fig_vehicle_growth.update_layout(template='plotly_white')
        plotly(fig_vehicle_growth)
else:
    text("*Not enough weekly data to calculate growth*")

# Show detailed data table with search capability - combine header and description
text("## 📋 Raw Data Explorer\nExplore the underlying data used in this dashboard. Showing records matching your filters.")

# Add options for pagination
display_rows = selectbox("Records to display:", ["20", "50", "100"], default="20")
display_rows = int(display_rows)

search_term = text_input("Search by base number:", "")

display_df = filtered_df

if search_term:
    display_df = display_df[display_df['dispatching_base_number'].str.contains(search_term, case=False)]
    text(f"Found {len(display_df):,} records containing '{search_term}'")

# Display only the key columns for better readability
# Convert date to string for display in the table
display_df_table = display_df.copy()
display_df_table['date'] = display_df_table['date'].dt.strftime('%Y-%m-%d')
display_columns = ['date', 'dispatching_base_number', 'active_vehicles', 'trips', 'trips_per_vehicle', 'day_type']
table(display_df_table[display_columns].sort_values('date', ascending=False).head(display_rows))

# Add a count summary
text(f"*Displaying {min(display_rows, len(display_df)):,} of {len(display_df):,} records. " + 
     f"Total records in dataset: {len(uber_df):,}*")
