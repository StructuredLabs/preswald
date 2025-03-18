#!/usr/bin/env python

import pandas as pd
from preswald import text, plotly, get_df, connect
import plotly.express as px
import plotly.graph_objects as go

connect()

# Load the dataset
df = get_df('smartphone_usage')

# Define a refined, aesthetic color palette
custom_colors = {
    "background": "#FFFFFF",     
    "text": "#2C3E50",           
    "primary": "#2E86AB",        
    "secondary": "#F6A01A",      
    "accent": "#F26419",        
    "neutral": "#95A5A6"         
}

# ---------------------------------------------------------------------------
# Front Dashboard: The Data Story
# ---------------------------------------------------------------------------
text("# Smartphone Usage Trends Dashboard")
text("Welcome to the ultimate story of smartphone usage. "
     "This dashboard weaves together key insights—ranging from overall app engagement, "
     "age-driven screen time patterns, to regional trends—providing a comprehensive narrative "
     "that reveals how our users interact with their digital world.")

# ---------------------------------------------------------------------------
# Section 1: Overall App Engagement
# ---------------------------------------------------------------------------
text("## Overall App Engagement")
fig_usage_dist = px.histogram(
    df,
    x='Total_App_Usage_Hours',
    nbins=30,
    title="Distribution of Total App Usage Hours",
    opacity=0.7,
    color_discrete_sequence=[custom_colors["primary"]]
)
fig_usage_dist.update_layout(
    title_font=dict(color=custom_colors["text"]),
    plot_bgcolor=custom_colors["background"],
    paper_bgcolor=custom_colors["background"]
)
# Set axis titles explicitly
fig_usage_dist.update_xaxes(title_text="Total App Usage Hours")
fig_usage_dist.update_yaxes(title_text="Frequency")
plotly(fig_usage_dist)

# ---------------------------------------------------------------------------
# Section 2: Screen Time Across Age Groups
# ---------------------------------------------------------------------------
text("## Screen Time Across Age Groups")
df['Age_Group'] = pd.cut(df['Age'], bins=[0, 18, 35, 50, 65, 100], labels=["<18", "18-35", "36-50", "51-65", "65+"])
df_age_trend = df.groupby('Age_Group')['Daily_Screen_Time_Hours'].mean().reset_index()
fig_age_trend = px.line(
    df_age_trend, 
    x='Age_Group', 
    y='Daily_Screen_Time_Hours', 
    markers=True,
    title='Average Daily Screen Time by Age Group',
    color_discrete_sequence=[custom_colors["secondary"]]
)
fig_age_trend.update_layout(
    title_font=dict(color=custom_colors["text"]),
    plot_bgcolor=custom_colors["background"],
    paper_bgcolor=custom_colors["background"]
)
# Set axis titles explicitly
fig_age_trend.update_xaxes(title_text="Age Group")
fig_age_trend.update_yaxes(title_text="Avg. Daily Screen Time (Hours)")
plotly(fig_age_trend)

# ---------------------------------------------------------------------------
# Section 3: App Usage Composition
# ---------------------------------------------------------------------------
text("## App Usage Composition")
usage_totals = df[['Social_Media_Usage_Hours', 'Productivity_App_Usage_Hours', 'Gaming_App_Usage_Hours']].sum().reset_index()
usage_totals.columns = ['Category', 'Total Hours']
fig_app_usage = px.bar(
    usage_totals,
    x='Category',
    y='Total Hours',
    title="Total Hours Spent on Each App Category",
    color='Category',
    color_discrete_sequence=[custom_colors["accent"], custom_colors["secondary"], custom_colors["primary"]]
)
fig_app_usage.update_layout(
    title_font=dict(color=custom_colors["text"]),
    plot_bgcolor=custom_colors["background"],
    paper_bgcolor=custom_colors["background"]
)
# Set axis titles explicitly
fig_app_usage.update_xaxes(title_text="App Category")
fig_app_usage.update_yaxes(title_text="Total Hours")
plotly(fig_app_usage)

# ---------------------------------------------------------------------------
# Section 4: Regional Trends - Mapping City Data to States
# ---------------------------------------------------------------------------
city_to_state = {
    "Los Angeles": "CA", "San Francisco": "CA", "San Diego": "CA", "Sacramento": "CA",
    "New York": "NY", "Buffalo": "NY", "Rochester": "NY",
    "Chicago": "IL", "Houston": "TX", "Austin": "TX", "Dallas": "TX",
    "Miami": "FL", "Orlando": "FL", "Tampa": "FL",
    "Atlanta": "GA", "Seattle": "WA", "Denver": "CO", "Boston": "MA",
    "Phoenix": "AZ", "Las Vegas": "NV", "Philadelphia": "PA"
}
df["State"] = df["Location"].map(city_to_state)
df = df.dropna(subset=["State"])
df_region = df.groupby("State").agg(
    avg_screen_time=("Daily_Screen_Time_Hours", "mean"),
    total_usage=("Total_App_Usage_Hours", "sum")
).reset_index()

text("## Regional Trends")
fig_map = px.choropleth(
    df_region,
    locations="State",
    locationmode="USA-states",
    color="avg_screen_time",
    title="Average Daily Screen Time by State",
    color_continuous_scale="Blues",
    labels={"avg_screen_time": "Avg Screen Time (Hours)"},
    scope="usa",
    range_color=(df_region["avg_screen_time"].min(), df_region["avg_screen_time"].max())
)
fig_map.update_layout(
    title_font=dict(color=custom_colors["text"]),
    plot_bgcolor=custom_colors["background"],
    paper_bgcolor=custom_colors["background"]
)
plotly(fig_map)
