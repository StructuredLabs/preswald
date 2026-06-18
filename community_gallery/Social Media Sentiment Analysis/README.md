# Social Media Sentiment Analysis Dashboard

A Preswald app that analyzes sentiment patterns in social media posts across different platforms and regions.

## Overview

This dashboard provides interactive visualizations and insights into social media sentiment data, allowing users to explore patterns across platforms, countries, and engagement levels. The app processes and normalizes data to reveal meaningful trends in social media sentiment.

## Features

- **Interactive Filtering**: Filter data by engagement level (likes)
- **Key Metrics Summary**: Quick overview of important statistics
- **Sample Post Display**: View representative posts from the dataset
- **Normalized Visualizations**: All charts use percentages or averages for better comparisons
- **Cross-Platform Analysis**: Compare sentiment across different social media platforms
- **Geographic Insights**: Analyze sentiment patterns by country
- **Engagement Metrics**: Understand the relationship between sentiment and user engagement

## Data Processing

The app performs several data processing steps:

1. **Data Cleaning**: Standardizes sentiment values, platform names, and country names
2. **Sentiment Scoring**: Converts categorical sentiment (Positive, Neutral, Negative) to numeric scores (1, 0, -1)
3. **Normalization**: Calculates percentages and averages for comparable visualizations
4. **Aggregation**: Groups data by various dimensions (sentiment, platform, country)
5. **Sampling**: Presents a representative sample of posts rather than the entire dataset

## Visualizations

### 1. Key Metrics

Provides at-a-glance summary of:
- Total number of posts in filtered dataset
- Average sentiment score with qualitative label (Positive, Neutral, Negative)
- Average engagement (likes) per post

### 2. Sentiment Distribution

- **Type**: Donut chart
- **Data**: Percentage breakdown of positive, neutral, and negative sentiment
- **Insights**: Shows the overall sentiment distribution in the dataset
- **Features**: Color-coded with percentage labels

### 3. Normalized Sentiment by Platform

- **Type**: 100% stacked bar chart
- **Data**: Percentage of each sentiment type within each platform
- **Insights**: Allows comparison of sentiment distribution across platforms regardless of post volume
- **Features**: Color-coded by sentiment with percentage labels

### 4. Engagement Analysis

- **Type**: Grouped bar chart
- **Data**: Average likes and retweets for each sentiment category
- **Insights**: Shows which sentiment types generate more engagement
- **Features**: Separate bars for likes and retweets for easy comparison

### 5. Geographic Sentiment Analysis

- **Type**: Horizontal bar chart
- **Data**: Average sentiment score by country
- **Insights**: Reveals regional differences in sentiment patterns
- **Features**: Color gradient based on sentiment score, sorted from most positive to most negative

## Using the App

### Filtering Data

Use the "Minimum Engagement" slider to filter posts based on their number of likes. This allows you to:
- Focus on high-engagement content
- See how sentiment patterns change with engagement levels
- Filter out low-engagement posts that might skew results

### Interpreting the Visualizations

- **Sentiment Score**: Ranges from -1 (Negative) to 1 (Positive), with 0 being Neutral
- **Percentages**: All charts show proportions rather than raw counts for better comparison
- **Color Coding**: Consistent colors are used throughout (Green = Positive, Yellow = Neutral, Red = Negative)

## Setup and Requirements

- **Python Version**: Python 3.7+ recommended
- **Required Packages**: preswald, pandas, plotly, numpy
- **Data Source**: Uses the sentiment_data CSV configured in preswald.toml

## Customization Options

You can customize the app by:

1. **Adjusting Thresholds**:
   - Sentiment classification thresholds can be modified in the key metrics section
   - Default engagement filter values can be adjusted

2. **Color Schemes**:
   - Sentiment colors are defined in the sentiment_colors dictionary
   - Visualization-specific colors can be modified in each chart's configuration

3. **Data Columns**:
   - Sample table columns can be adjusted to show different attributes
   - Additional filters can be added by creating new slider components

## Technical Implementation

The app uses several advanced techniques:

- **Pandas Pivot Tables**: For cross-tabulation and normalization
- **Custom Color Scales**: For meaningful visual encoding of data
- **Dynamic Filtering**: Real-time data filtering based on user input
- **Statistical Aggregation**: Calculating means and distributions on the fly

## Getting Started

### Prerequisites

- Python 3.7+
- Preswald package (`pip install preswald`)
- Additional packages: pandas, plotly, numpy

### Running the App

To run the app locally, navigate to the project directory and use:

```bash
preswald run
```

The app will be accessible at http://localhost:8501 by default.

### Project Structure

- `app.py` - Main application file with visualizations and data processing
- `preswald.toml` - Configuration file for the project and data sources
- `data/` - Directory containing the sentiment dataset

## Data Source

The sentiment analysis dataset includes the following fields:

- **Text**: Content of the social media post
- **Sentiment**: Classification as Positive, Neutral, or Negative
- **Platform**: Social media platform (Twitter, Facebook, Instagram, etc.)
- **Timestamp**: When the post was created
- **User**: Username of the poster
- **Hashtags**: Hashtags used in the post
- **Likes**: Number of likes/reactions
- **Retweets**: Number of retweets/shares
- **Country**: Country of origin
- **Year, Month, Day, Hour**: Time components extracted from the timestamp

## Further Development

Potential enhancements for future versions:

1. **Time-Series Analysis**: Add visualizations showing sentiment changes over time
2. **Topic Modeling**: Extract and visualize key topics from post content
3. **Predictive Analytics**: Add sentiment prediction for new content
4. **Additional Filters**: Enable filtering by platform, country, and date range
5. **Export Capabilities**: Allow exporting of insights and filtered data 



Custom domain assigned at sentiment-analysis-y0fpbtgl.preswald.app
App is available here https://sentiment-analysis-y0fpbtgl-ndjz2ws6la-ue.a.run.app
Custom domain assigned at sentiment-analysis-y0fpbtgl.preswald.app