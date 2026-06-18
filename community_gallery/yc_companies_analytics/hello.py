from preswald import text, plotly, connect, get_df, table, slider, separator
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is YC companies latest data analysis(2000-2025).")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('yc_companies_csv')
table(df.head(10))

# Data cleaning and preparation
df['teamSize'] = pd.to_numeric(df['teamSize'], errors='coerce').fillna(0)
df['industries'] = df['industries'].str.split(', ')
df['locations'] = df['locations'].str.split(', ')

# Exploded versions for analysis
industries_df = df.explode('industries')
locations_df = df.explode('locations')

# --- 1. Company Distribution by Batch ---
separator()
text("## 1. Company Distribution by Batch")

# Bar chart for batch distribution
batch_counts = df['batch'].value_counts().reset_index()
batch_counts.columns = ['batch', 'count']
batch_chart = px.bar(batch_counts, x='batch', y='count', title="Companies by Batch")
plotly(batch_chart)

# Statistical insights
avg_companies_per_batch = batch_counts['count'].mean()
text(f"**Average companies per batch:** {avg_companies_per_batch:.1f}")

# --- 2. Team Size Distribution ---
separator()
text("## 2. Team Size Distribution")

# Slider for team size filtering
team_size_filter = slider("Filter by Team Size", 0, int(df['teamSize'].max()), 0)

# Filter data
filtered_df = df[df['teamSize'] >= team_size_filter]

# Histogram for team size distribution
team_size_hist = px.histogram(
    filtered_df,
    x='teamSize',
    nbins=20,
    title="Team Size Distribution",
    labels={'teamSize': 'Team Size'}
)
plotly(team_size_hist)

# Statistical insights
mean_team_size = filtered_df['teamSize'].mean()
median_team_size = filtered_df['teamSize'].median()
text(f"**Mean Team Size:** {mean_team_size:.1f}")
text(f"**Median Team Size:** {median_team_size:.1f}")

# --- 3. Industry Breakdown ---
separator()
text("## 3. Industry Breakdown")

# Top 10 industries bar chart
top_industries = industries_df['industries'].value_counts().nlargest(10).reset_index()
top_industries.columns = ['industry', 'count']
industry_bar = px.bar(
    top_industries,
    x='industry',
    y='count',
    title="Top 10 Industries"
)
plotly(industry_bar)

# Statistical insights
total_companies = len(df)
industry_percentages = (top_industries['count'] / total_companies * 100).round(1)
text("**Top Industries and Their Percentages:**")
for industry, percentage in zip(top_industries['industry'], industry_percentages):
    industry_text = "\n".join(f"- {industry}: {percentage}%" 
                                  for industry, percentage in zip(top_industries["industry"], industry_percentages))

# --- 4. Company Status Analysis ---
separator()
text("## 4. Company Status Analysis")

# Pie chart for status distribution
status_pie = px.pie(
    df,
    names='status',
    title="Company Status Distribution",
    hole=0.4
)
plotly(status_pie)

# Statistical insights - Status Distribution
status_counts = df['status'].value_counts()
status_percentages = (status_counts / total_companies * 100).round(1)

if not status_percentages.empty:  # Proper way to check if Series has data
    text("**Status Distribution:**")
    status_text = "\n".join(f"- {status}: {percentage}%" for status, percentage in status_percentages.items())
    text(status_text)


# --- 5. Location Analysis ---
separator()
text("## 5. Location Analysis")

# Top 10 locations bar chart
top_locations = locations_df['locations'].value_counts().nlargest(10).reset_index()
top_locations.columns = ['location', 'count']
location_bar = px.bar(
    top_locations,
    x='location',
    y='count',
    title="Top 10 Locations"
)
plotly(location_bar)


# Ensure 'count' column is numeric and total_companies is not zero
if total_companies > 0 and 'count' in top_locations.columns:
    location_percentages = (top_locations['count'] / total_companies * 100).round(1)
    text("**Top Locations and Their Percentages:**")
    if not top_locations.empty:
        location_text = "\n".join(f"- {location}: {percentage}%" 
                                  for location, percentage in zip(top_locations['location'], location_percentages))
        text(location_text)
    else:
        text("No location data available.")
else:
    text("Total companies count is zero or invalid data structure.")

