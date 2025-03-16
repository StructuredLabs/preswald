import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from collections import Counter

from preswald import (
    connect, 
    get_df, 
    plotly, 
    slider, 
    table, 
    text
)

# App title and description
text("# Social Media Sentiment Analysis")
text("Explore normalized sentiment patterns across platforms and regions")

# Connect to data source defined in preswald.toml
connect()
df = get_df('sentiment_data')

# Clean up dataset
df['Sentiment'] = df['Sentiment'].str.strip()
df['Platform'] = df['Platform'].str.strip()
df['Country'] = df['Country'].str.strip()
df['Timestamp_dt'] = pd.to_datetime(df['Timestamp'])

# Add a sentiment score column (for visualization purposes)
sentiment_scores = {'Positive': 1, 'Neutral': 0, 'Negative': -1}
df['SentimentScore'] = df['Sentiment'].map(sentiment_scores)

# Create a simple filter
text("## Filter Data")

# Simple slider for minimum engagement
min_engagement = slider(
    "Minimum Engagement (Likes)",
    min_val=float(0),
    max_val=float(100),
    default=float(0)
)

# Filter data based on likes
filtered_df = df[df['Likes'] >= min_engagement]

# Display key metrics at the top
total_posts = len(filtered_df)
avg_sentiment = filtered_df['SentimentScore'].mean()
sentiment_status = "Positive" if avg_sentiment > 0.2 else "Neutral" if avg_sentiment > -0.2 else "Negative"
avg_engagement = filtered_df['Likes'].mean()

text(f"### Key Metrics")
text(f"📊 Total Posts: {total_posts}  |  📈 Average Sentiment: {sentiment_status} ({avg_sentiment:.2f})  |  ❤️ Average Engagement: {avg_engagement:.1f} likes")

# Display a sample of the filtered data
text("## Sample Social Media Posts")
sample_df = filtered_df.sample(min(5, len(filtered_df))) if len(filtered_df) > 0 else filtered_df
table(sample_df[['Text', 'Sentiment', 'Platform', 'Likes', 'Country']], 
      title="Sample Posts")

# Show normalized sentiment distribution
text("## Sentiment Analysis")

# Calculate sentiment percentages directly
sentiment_counts = filtered_df['Sentiment'].value_counts()
total = sentiment_counts.sum()
sentiment_df = pd.DataFrame({
    'Sentiment': sentiment_counts.index,
    'Count': sentiment_counts.values,
    'Percentage': (sentiment_counts.values / total * 100).round(1)
})

sentiment_colors = {
    'Positive': '#4CAF50',
    'Neutral': '#FFC107',
    'Negative': '#F44336'
}

sentiment_fig = px.pie(
    sentiment_df, 
    values='Percentage', 
    names='Sentiment',
    title='Sentiment Distribution (%)',
    color='Sentiment',
    color_discrete_map=sentiment_colors,
    hole=0.4
)

# Add percentage labels
sentiment_fig.update_traces(textposition='inside', textinfo='percent+label')
plotly(sentiment_fig)

# Normalized sentiment by platform (100% stacked bar)
text("## Normalized Sentiment by Platform")
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

# Create 100% stacked bar chart
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

# Engagement by sentiment
text("## Engagement Analysis")
engagement_by_sentiment = filtered_df.groupby('Sentiment')[['Likes', 'Retweets']].mean().reset_index()

# Create a grouped bar chart for engagement metrics
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

# Sentiment by country (heatmap)
text("## Geographic Sentiment Analysis")
# Get normalized sentiment scores by country
country_sentiment = filtered_df.groupby('Country')['SentimentScore'].mean().reset_index()
country_sentiment = country_sentiment.sort_values('SentimentScore', ascending=False)

# Create a horizontal bar chart colored by sentiment score
country_fig = px.bar(
    country_sentiment,
    y='Country',
    x='SentimentScore',
    orientation='h',
    title='Average Sentiment Score by Country',
    color='SentimentScore',
    color_continuous_scale=[(0, '#F44336'), (0.5, '#FFC107'), (1, '#4CAF50')],
    range_color=[-1, 1],
    labels={'SentimentScore': 'Avg. Sentiment (-1 to 1)'}
)
country_fig.update_layout(yaxis={'categoryorder': 'total ascending'})
plotly(country_fig) 