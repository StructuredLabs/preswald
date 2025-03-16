import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from collections import Counter
# Removing wordcloud and matplotlib imports that cause deployment issues
# from wordcloud import WordCloud
# import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta

from preswald import (
    connect, 
    get_df, 
    plotly, 
    slider, 
    table, 
    text
)

# App title and description
text("# Social Media Sentiment Analysis Dashboard")
text("Comprehensive analysis of normalized sentiment patterns across social media platforms")

# Simple filter section
text("## Data Filter")
min_engagement = slider(
    "Minimum Engagement (Likes)",
    min_val=float(0),
    max_val=float(100),
    default=float(0)
)

# Connect to data source defined in preswald.toml
connect()
df = get_df('sentiment_data')

# Clean up dataset and add derived columns
df['Sentiment'] = df['Sentiment'].str.strip()
df['Platform'] = df['Platform'].str.strip()
df['Country'] = df['Country'].str.strip()
df['Timestamp_dt'] = pd.to_datetime(df['Timestamp'])
df['Date'] = df['Timestamp_dt'].dt.date
df['Week'] = df['Timestamp_dt'].dt.isocalendar().week
df['Weekday'] = df['Timestamp_dt'].dt.day_name()
df['Hour'] = df['Timestamp_dt'].dt.hour
df['Post_Length'] = df['Text'].str.len()

# Add sentiment and engagement scores
sentiment_scores = {'Positive': 1, 'Neutral': 0, 'Negative': -1}
df['SentimentScore'] = df['Sentiment'].map(sentiment_scores)
df['EngagementScore'] = df['Likes'] + df['Retweets']

# Filter data based on engagement slider
filtered_df = df[df['Likes'] >= min_engagement]

# Define color scheme for consistent visuals
sentiment_colors = {
    'Positive': '#4CAF50',
    'Neutral': '#FFC107',
    'Negative': '#F44336'
}

# ==================== DASHBOARD SECTIONS ====================

# ---- 1. KEY METRICS OVERVIEW ----
text("## 1. Key Metrics Overview")

# Display key metrics at the top
total_posts = len(filtered_df)
avg_sentiment = filtered_df['SentimentScore'].mean()
sentiment_status = "Positive" if avg_sentiment > 0.2 else "Neutral" if avg_sentiment > -0.2 else "Negative"
avg_engagement = filtered_df['Likes'].mean()
distinct_platforms = filtered_df['Platform'].nunique()
distinct_countries = filtered_df['Country'].nunique()

text(f"📊 Total Posts: {total_posts}")
text(f"📈 Average Sentiment: {sentiment_status} ({avg_sentiment:.2f})")
text(f"❤️ Average Engagement: {avg_engagement:.1f} likes")
text(f"🌐 Platforms: {distinct_platforms}")
text(f"🌍 Countries: {distinct_countries}")

# Sample data preview
text("### Sample Social Media Posts")
sample_df = filtered_df.sample(min(3, len(filtered_df))) if len(filtered_df) > 0 else filtered_df
table(sample_df[['Text', 'Sentiment', 'Platform', 'Likes', 'Country']], 
      title="Sample Posts")

# ---- 2. SENTIMENT DISTRIBUTION ----
text("## 2. Sentiment Distribution")

# Calculate sentiment percentages
sentiment_counts = filtered_df['Sentiment'].value_counts()
total = sentiment_counts.sum()
sentiment_df = pd.DataFrame({
    'Sentiment': sentiment_counts.index,
    'Count': sentiment_counts.values,
    'Percentage': (sentiment_counts.values / total * 100).round(1)
})

# Pie chart for sentiment distribution
sentiment_fig = px.pie(
    sentiment_df, 
    values='Percentage', 
    names='Sentiment',
    title='Sentiment Distribution (%)',
    color='Sentiment',
    color_discrete_map=sentiment_colors,
    hole=0.4
)
sentiment_fig.update_traces(textposition='inside', textinfo='percent+label')
plotly(sentiment_fig)

# Bar chart for sentiment counts
sentiment_bar = px.bar(
    sentiment_df,
    x='Sentiment',
    y='Count',
    color='Sentiment',
    color_discrete_map=sentiment_colors,
    title='Sentiment Distribution (Count)',
    text='Count'
)
sentiment_bar.update_traces(textposition='outside')
plotly(sentiment_bar)

# ---- 3. PLATFORM ANALYSIS ----
text("## 3. Platform Analysis")

# Platform distribution
platform_counts = filtered_df['Platform'].value_counts().reset_index()
platform_counts.columns = ['Platform', 'Count']

platform_fig = px.bar(
    platform_counts,
    x='Platform',
    y='Count',
    title='Posts by Platform',
    color='Platform'
)
plotly(platform_fig)

# Platform and sentiment snapshot
platform_sentiment = filtered_df.groupby('Platform')['SentimentScore'].mean().reset_index()
platform_engagement = filtered_df.groupby('Platform')['EngagementScore'].mean().reset_index()
platform_count = filtered_df['Platform'].value_counts().reset_index()
platform_count.columns = ['Platform', 'Count']

platform_combined = pd.merge(platform_sentiment, platform_engagement, on='Platform')
platform_combined = pd.merge(platform_combined, platform_count, on='Platform')

platform_bubble = px.scatter(
    platform_combined,
    x='SentimentScore',
    y='EngagementScore',
    size='Count',
    color='Platform',
    hover_name='Platform',
    title='Platform Comparison: Sentiment vs. Engagement',
    labels={
        'SentimentScore': 'Average Sentiment (-1 to 1)',
        'EngagementScore': 'Average Engagement (Likes + Retweets)',
        'Count': 'Number of Posts'
    }
)
plotly(platform_bubble)

# Normalized sentiment by platform
text("### Sentiment Distribution by Platform")

# First get counts
platform_sentiment = filtered_df.groupby(['Platform', 'Sentiment']).size().reset_index(name='Count')
# Then pivot and normalize
pivot_df = platform_sentiment.pivot_table(
    index='Platform', 
    columns='Sentiment', 
    values='Count', 
    fill_value=0
)
# Calculate percentages
platform_percentages = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100

# Convert back to long format for plotting
platform_pct_long = platform_percentages.reset_index().melt(
    id_vars='Platform',
    value_vars=platform_percentages.columns.tolist(),
    var_name='Sentiment',
    value_name='Percentage'
)

platform_sentiment_fig = px.bar(
    platform_pct_long,
    x='Platform',
    y='Percentage',
    color='Sentiment',
    title='Normalized Sentiment Distribution by Platform (%)',
    color_discrete_map=sentiment_colors,
    labels={'Percentage': 'Percentage (%)'},
    text_auto='.1f'
)
platform_sentiment_fig.update_layout(barmode='stack')
plotly(platform_sentiment_fig)

# ---- 4. ENGAGEMENT INSIGHTS ----
text("## 4. Engagement Insights")

# Engagement by sentiment
engagement_by_sentiment = filtered_df.groupby('Sentiment')[['Likes', 'Retweets', 'EngagementScore']].mean().reset_index()

engagement_fig = px.bar(
    engagement_by_sentiment,
    x='Sentiment',
    y=['Likes', 'Retweets'],
    title='Average Engagement by Sentiment',
    barmode='group',
    color_discrete_sequence=['#FF9800', '#2196F3'],
    labels={'value': 'Average Count', 'variable': 'Metric'}
)
plotly(engagement_fig)

# Engagement by day of week
text("### Engagement by Day of Week")
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
daily_engagement = filtered_df.groupby('Weekday')['EngagementScore'].mean().reset_index()

# Custom sort the weekdays
daily_engagement['Weekday'] = pd.Categorical(
    daily_engagement['Weekday'], 
    categories=day_order, 
    ordered=True
)
daily_engagement = daily_engagement.sort_values('Weekday')

day_fig = px.bar(
    daily_engagement,
    x='Weekday',
    y='EngagementScore',
    title='Average Engagement by Day of Week',
    color='EngagementScore',
    color_continuous_scale=[(0, '#E3F2FD'), (1, '#1565C0')],
    labels={'EngagementScore': 'Average Engagement (Likes + Retweets)'}
)
plotly(day_fig)

# Engagement by hour of day
text("### Engagement by Hour of Day")
hourly_engagement = filtered_df.groupby('Hour')['EngagementScore'].mean().reset_index()

hour_fig = px.line(
    hourly_engagement,
    x='Hour',
    y='EngagementScore',
    title='Average Engagement by Hour of Day',
    markers=True,
    labels={'EngagementScore': 'Average Engagement (Likes + Retweets)'}
)
hour_fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
plotly(hour_fig)

# ---- 5. GEOGRAPHIC ANALYSIS ----
text("## 5. Geographic Analysis")

# Posts by country
country_counts = filtered_df['Country'].value_counts().reset_index()
country_counts.columns = ['Country', 'Count']
country_counts = country_counts.sort_values('Count', ascending=False)

country_fig = px.bar(
    country_counts.head(10),
    x='Country',
    y='Count',
    title='Top 10 Countries by Post Volume',
    color='Count',
    color_continuous_scale=[(0, '#E3F2FD'), (1, '#1565C0')],
)
plotly(country_fig)

# Sentiment by country
text("### Sentiment Analysis by Country")
country_sentiment = filtered_df.groupby('Country')['SentimentScore'].mean().reset_index()
country_sentiment = country_sentiment.sort_values('SentimentScore', ascending=False)

country_sentiment_fig = px.bar(
    country_sentiment.head(10),
    y='Country',
    x='SentimentScore',
    orientation='h',
    title='Average Sentiment Score by Country (Top 10)',
    color='SentimentScore',
    color_continuous_scale=[(0, '#F44336'), (0.5, '#FFC107'), (1, '#4CAF50')],
    range_color=[-1, 1],
    labels={'SentimentScore': 'Avg. Sentiment (-1 to 1)'}
)
country_sentiment_fig.update_layout(yaxis={'categoryorder': 'total ascending'})
plotly(country_sentiment_fig)

# ---- 6. TIME TRENDS ----
text("## 6. Trend Analysis")

# Sentiment trends over time
time_sentiment = filtered_df.groupby(['Date', 'Sentiment']).size().reset_index(name='Count')

time_fig = px.line(
    time_sentiment,
    x='Date',
    y='Count',
    color='Sentiment',
    title='Sentiment Trends Over Time',
    color_discrete_map=sentiment_colors,
    markers=True
)
plotly(time_fig)

# Platform activity over time
text("### Platform Activity Over Time")
platform_time = filtered_df.groupby(['Date', 'Platform']).size().reset_index(name='Count')

platform_time_fig = px.line(
    platform_time,
    x='Date',
    y='Count',
    color='Platform',
    title='Platform Activity Over Time',
    markers=True
)
plotly(platform_time_fig)

# Close with summary
text("## Dashboard Summary")
text("This dashboard provides a comprehensive view of social media sentiment across platforms, regions, and time periods. Key insights include sentiment distribution, platform engagement patterns, and geographic trends.")
text("Filter the data using the engagement slider at the top to focus on posts with higher engagement levels.") 