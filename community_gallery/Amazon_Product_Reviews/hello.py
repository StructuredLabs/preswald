from preswald import text, plotly, connect, get_df, table, slider, selectbox
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from collections import Counter

# Dashboard header with improved styling
text("# 📊 Amazon Product Reviews Analytics")
text("### Interactive dashboard for customer sentiment analysis and product performance insights")

# Connect to data source
connect()

# Load the dataset with proper error handling
reviews_df = get_df('reviews')

# Check if data loaded properly
if reviews_df is None:
    text("⚠️ **Error: Unable to load the Reviews dataset.**")
    text("Please make sure:")
    text("1. The file 'Reviews.csv' is properly uploaded")
    text("2. The Preswald connection is configured correctly")
    text("3. Check the CSV file format and encoding")
else:
    # Display data info
    text(f"**Dataset Overview:** {len(reviews_df):,} reviews analyzed")
    
    # Basic data cleaning
    # Convert numeric columns if needed
    numeric_cols = ['HelpfulnessNumerator', 'HelpfulnessDenominator', 'Score', 'Time']
    for col in numeric_cols:
        if col in reviews_df.columns:
            reviews_df[col] = pd.to_numeric(reviews_df[col], errors='coerce')
    
    # Convert timestamp to datetime if Time column exists
    if 'Time' in reviews_df.columns:
        reviews_df['Date'] = pd.to_datetime(reviews_df['Time'], unit='s')
        reviews_df['Year'] = reviews_df['Date'].dt.year
        reviews_df['Month'] = reviews_df['Date'].dt.month
        reviews_df['YearMonth'] = reviews_df['Date'].dt.strftime('%Y-%m')
        reviews_df['DayOfWeek'] = reviews_df['Date'].dt.dayofweek
    
    # Calculate review text length if Text column exists
    if 'Text' in reviews_df.columns:
        reviews_df['ReviewLength'] = reviews_df['Text'].apply(lambda x: len(str(x)))
    
    # Calculate helpfulness ratio if needed columns exist
    if 'HelpfulnessNumerator' in reviews_df.columns and 'HelpfulnessDenominator' in reviews_df.columns:
        reviews_df['HelpfulnessRatio'] = reviews_df.apply(
            lambda x: x['HelpfulnessNumerator'] / x['HelpfulnessDenominator'] 
            if x['HelpfulnessDenominator'] > 0 else 0, 
            axis=1
        )
    
    # Add sentiment classification based on ratings
    if 'Score' in reviews_df.columns:
        reviews_df['Sentiment'] = reviews_df['Score'].apply(
            lambda x: 'Positive' if x >= 4 
                     else ('Neutral' if x == 3 
                          else 'Negative')
        )
    
    # Display key metrics at the top in a clean, visual way
    if 'Score' in reviews_df.columns:
        # Calculate key metrics
        avg_rating = reviews_df['Score'].mean()
        pct_positive = (reviews_df['Score'] >= 4).mean() * 100
        pct_negative = (reviews_df['Score'] <= 2).mean() * 100
        
        # Display metrics in a more visual way
        text("## 📈 Key Metrics")
        
        # Create a figure with 3 subplots for key metrics
        fig_metrics = go.Figure()
        
        # Average Rating Gauge
        fig_metrics.add_trace(go.Indicator(
            mode = "gauge+number",
            value = avg_rating,
            title = {'text': "Average Rating"},
            domain = {'x': [0, 0.32], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 5], 'tickwidth': 1},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [0, 2], 'color': "#ffcccb"},
                    {'range': [2, 3.5], 'color': "#ffffcc"},
                    {'range': [3.5, 5], 'color': "#ccffcc"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 2},
                    'thickness': 0.75,
                    'value': avg_rating
                }
            }
        ))
        
        # Positive Reviews Percentage
        fig_metrics.add_trace(go.Indicator(
            mode = "gauge+number",
            value = pct_positive,
            title = {'text': "Positive Reviews (%)"},
            domain = {'x': [0.34, 0.66], 'y': [0, 1]},
            number = {'suffix': "%"},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#2ca02c"},
                'steps': [
                    {'range': [0, 50], 'color': "#ffcccb"},
                    {'range': [50, 75], 'color': "#ffffcc"},
                    {'range': [75, 100], 'color': "#ccffcc"}
                ],
                'threshold': {
                    'line': {'color': "green", 'width': 2},
                    'thickness': 0.75,
                    'value': pct_positive
                }
            }
        ))
        
        # Negative Reviews Percentage
        fig_metrics.add_trace(go.Indicator(
            mode = "gauge+number",
            value = pct_negative,
            title = {'text': "Negative Reviews (%)"},
            domain = {'x': [0.68, 1], 'y': [0, 1]},
            number = {'suffix': "%"},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#d62728"},
                'steps': [
                    {'range': [0, 10], 'color': "#ccffcc"},
                    {'range': [10, 25], 'color': "#ffffcc"},
                    {'range': [25, 100], 'color': "#ffcccb"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 2},
                    'thickness': 0.75,
                    'value': pct_negative
                }
            }
        ))
        
        fig_metrics.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        
        plotly(fig_metrics)
    
    # Control section
    text("## 🔍 Filters")
    
    # Create filter controls
    if 'Score' in reviews_df.columns:
        min_score = slider("Minimum Rating Filter", min_val=1, max_val=5, default=1)
        
        # Add sentiment filter
        sentiment_options = ["All", "Positive", "Neutral", "Negative"]
        selected_sentiment = selectbox("Filter by Sentiment", options=sentiment_options, default="All")
        
        # Apply filters
        filtered_df = reviews_df[reviews_df['Score'] >= min_score]
        
        if selected_sentiment != "All":
            filtered_df = filtered_df[filtered_df['Sentiment'] == selected_sentiment]
        
        # Show filter summary
        text(f"**Applied Filters:** Showing {len(filtered_df):,} reviews with rating ≥ {min_score}" + 
             (f" and {selected_sentiment} sentiment" if selected_sentiment != "All" else ""))
    else:
        filtered_df = reviews_df
        text("⚠️ Score column not found. Showing all data without filtering.")
    
    # Show sample data
    text("## 📋 Sample Reviews")
    table(filtered_df.head(5), title="Preview of Filtered Reviews")
    
    # Only continue with visualizations if we have the required columns
    if 'Score' in reviews_df.columns:
        # Visualization: Sentiment Distribution with improved visuals
        text("## 😊 Sentiment Analysis")
        
        # Create sentiment counts
        sentiment_counts = filtered_df['Sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        
        # Define custom colors for sentiments
        sentiment_colors = {
            'Positive': '#2ca02c',  # Green
            'Neutral': '#d3d3d3',   # Light gray
            'Negative': '#d62728'   # Red
        }
        
        # Create pie chart for sentiment distribution
        fig_sentiment = px.pie(
            sentiment_counts, 
            values='Count', 
            names='Sentiment',
            title='Distribution of Review Sentiments',
            color='Sentiment',
            color_discrete_map=sentiment_colors,
            hole=0.4
        )
        
        fig_sentiment.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hoverinfo='label+percent+value'
        )
        
        fig_sentiment.update_layout(
            legend_title_text='Sentiment',
            height=400
        )
        
        plotly(fig_sentiment)
        
        # Add insights about sentiment
        positive_pct = (filtered_df['Sentiment'] == 'Positive').mean() * 100
        text(f"**💡 Insight:** {positive_pct:.1f}% of reviews express positive sentiment. " + 
             ("This indicates strong customer satisfaction overall." if positive_pct > 70 else 
              "There may be opportunities to improve customer satisfaction." if positive_pct < 50 else
              "Customer satisfaction is moderate and could be improved."))
        
        # Visualization: Score Distribution with better visuals
        text("## ⭐ Rating Distribution")
        
        # Calculate score counts and percentages
        score_counts = filtered_df['Score'].value_counts().sort_index().reset_index()
        score_counts.columns = ['Score', 'Count']
        score_counts['Percentage'] = score_counts['Count'] / score_counts['Count'].sum() * 100
        
        # Create a custom color scale based on the rating
        custom_colors = ['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a']
        
        # Create a dual-axis bar chart with percentages
        fig_scores = go.Figure()
        
        # Add bars for counts
        fig_scores.add_trace(go.Bar(
            x=score_counts['Score'],
            y=score_counts['Count'],
            name='Count',
            marker_color=custom_colors,
            text=score_counts['Count'],
            textposition='auto'
        ))
        
        # Add line for percentages
        fig_scores.add_trace(go.Scatter(
            x=score_counts['Score'],
            y=score_counts['Percentage'],
            name='Percentage',
            mode='lines+markers',
            yaxis='y2',
            line=dict(color='#000000', width=2),
            marker=dict(size=8)
        ))
        
        # Update layout with dual y-axes
        fig_scores.update_layout(
            title='Distribution of Ratings',
            xaxis=dict(
                title='Rating',
                tickmode='linear',
                tick0=1,
                dtick=1
            ),
            yaxis=dict(
                title='Count',
                side='left'
            ),
            yaxis2=dict(
                title='Percentage (%)',
                side='right',
                overlaying='y',
                showgrid=False
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ),
            barmode='group',
            height=500
        )
        
        plotly(fig_scores)
        
        # Add statistics and insights
        avg_score = filtered_df['Score'].mean()
        median_score = filtered_df['Score'].median()
        mode_score = filtered_df['Score'].mode()[0]
        
        text(f"**Rating Statistics:** Average: {avg_score:.2f} | Median: {median_score} | Most Common: {mode_score}")
        
        # Add insight based on rating distribution
        top_two_pct = (filtered_df['Score'] >= 4).mean() * 100
        lowest_two_pct = (filtered_df['Score'] <= 2).mean() * 100
        
        if top_two_pct > 70:
            text("**💡 Insight:** The high percentage of 4-5 star ratings suggests strong customer satisfaction.")
        elif lowest_two_pct > 30:
            text("**💡 Insight:** The significant percentage of 1-2 star ratings indicates potential product or service issues.")
        else:
            text("**💡 Insight:** The mixed rating distribution suggests varying customer experiences.")
        
        # Visualization: Review Length vs Score with enhanced visuals
        if 'ReviewLength' in filtered_df.columns:
            text("## 📝 Review Length Analysis")
            
            # Calculate average review length by score for bar chart
            avg_lengths = filtered_df.groupby('Score')['ReviewLength'].mean().reset_index()
            
            # Create a more informative combined visualization
            fig_length = go.Figure()
            
            # Add box plots
            for score in sorted(filtered_df['Score'].unique()):
                score_data = filtered_df[filtered_df['Score'] == score]['ReviewLength']
                
                fig_length.add_trace(go.Box(
                    y=score_data,
                    name=f"{score} ★",
                    boxpoints='outliers',
                    jitter=0.3,
                    pointpos=-1.8,
                    boxmean=True,
                    marker_color=custom_colors[int(score)-1] if 1 <= score <= 5 else '#1f77b4'
                ))
            
            fig_length.update_layout(
                title='Review Length by Rating',
                xaxis_title='Rating',
                yaxis_title='Review Length (characters)',
                boxmode='group',
                height=600,
                showlegend=False
            )
            
            plotly(fig_length)
            
            # Add statistics and insights
            avg_positive_length = filtered_df[filtered_df['Score'] >= 4]['ReviewLength'].mean()
            avg_negative_length = filtered_df[filtered_df['Score'] <= 2]['ReviewLength'].mean()
            
            text("**Average Review Length by Sentiment:**")
            text(f"- Positive reviews (4-5★): {avg_positive_length:.0f} characters")
            text(f"- Negative reviews (1-2★): {avg_negative_length:.0f} characters")
            
            if avg_negative_length > avg_positive_length:
                length_diff_pct = (avg_negative_length / avg_positive_length - 1) * 100
                text(f"**💡 Insight:** Negative reviews are {length_diff_pct:.0f}% longer than positive ones. Customers tend to be more detailed when expressing dissatisfaction.")
            else:
                length_diff_pct = (avg_positive_length / avg_negative_length - 1) * 100
                text(f"**💡 Insight:** Positive reviews are {length_diff_pct:.0f}% longer than negative ones. Satisfied customers are sharing more detailed experiences.")
            
            # Show a table with statistics
            length_stats = filtered_df.groupby('Score')['ReviewLength'].agg(['mean', 'median', 'min', 'max']).reset_index()
            length_stats.columns = ['Rating', 'Average Length', 'Median Length', 'Minimum Length', 'Maximum Length']
            length_stats = length_stats.round(0)
            
            table(length_stats, title="Review Length Statistics by Rating")
        
        # Visualization: Helpfulness Analysis with better insights
        if 'HelpfulnessRatio' in filtered_df.columns:
            text("## 👍 Review Helpfulness Analysis")
            
            # Create helpfulness by score dataset
            helpfulness_by_score = filtered_df.groupby('Score')['HelpfulnessRatio'].mean().reset_index()
            
            # Create a bar chart for average helpfulness by score
            fig_helpful = px.bar(
                helpfulness_by_score,
                x='Score',
                y='HelpfulnessRatio',
                title='Average Helpfulness Ratio by Rating',
                labels={'Score': 'Rating', 'HelpfulnessRatio': 'Average Helpfulness Ratio'},
                color='Score',
                color_continuous_scale='Viridis',
                text=helpfulness_by_score['HelpfulnessRatio'].round(2)
            )
            
            fig_helpful.update_layout(
                xaxis=dict(
                    tickmode='linear',
                    tick0=1,
                    dtick=1
                ),
                yaxis=dict(
                    title='Helpfulness Ratio',
                    range=[0, 1]
                ),
                height=400,
                coloraxis_showscale=False
            )
            
            # Add text annotations
            fig_helpful.update_traces(
                texttemplate='%{text:.2f}',
                textposition='outside'
            )
            
            plotly(fig_helpful)
            
            # Add helpfulness by review length analysis
            text("### Helpfulness by Review Length")
            
            # Create bins for review length
            if 'ReviewLength' in filtered_df.columns:
                filtered_df['LengthBin'] = pd.cut(
                    filtered_df['ReviewLength'],
                    bins=[0, 100, 250, 500, 1000, float('inf')],
                    labels=['Very Short (<100)', 'Short (100-250)', 'Medium (250-500)', 'Long (500-1000)', 'Very Long (>1000)']
                )
                
                # Calculate average helpfulness by length bin
                helpful_by_length = filtered_df.groupby('LengthBin')['HelpfulnessRatio'].mean().reset_index()
                helpful_by_length['Count'] = filtered_df.groupby('LengthBin').size().values
                
                # Create a dual-axis chart
                fig_helpful_length = go.Figure()
                
                # Add bars for helpfulness ratio
                fig_helpful_length.add_trace(go.Bar(
                    x=helpful_by_length['LengthBin'],
                    y=helpful_by_length['HelpfulnessRatio'],
                    name='Helpfulness Ratio',
                    marker_color='#1f77b4',
                    text=helpful_by_length['HelpfulnessRatio'].round(2),
                    textposition='outside'
                ))
                
                # Add line for count
                fig_helpful_length.add_trace(go.Scatter(
                    x=helpful_by_length['LengthBin'],
                    y=helpful_by_length['Count'],
                    name='Review Count',
                    mode='lines+markers',
                    yaxis='y2',
                    line=dict(color='#ff7f0e', width=2),
                    marker=dict(size=8)
                ))
                
                fig_helpful_length.update_layout(
                    title='Helpfulness Ratio by Review Length',
                    xaxis=dict(title='Review Length'),
                    yaxis=dict(
                        title='Helpfulness Ratio',
                        range=[0, max(helpful_by_length['HelpfulnessRatio']) * 1.2]
                    ),
                    yaxis2=dict(
                        title='Number of Reviews',
                        overlaying='y',
                        side='right',
                        showgrid=False
                    ),
                    legend=dict(
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='center',
                        x=0.5
                    ),
                    height=400
                )
                
                plotly(fig_helpful_length)
                
                # Add insights
                most_helpful_length = helpful_by_length.loc[helpful_by_length['HelpfulnessRatio'].idxmax()]['LengthBin']
                text(f"**💡 Insight:** {most_helpful_length} reviews tend to be rated as most helpful by other customers.")
            
            # Calculate correlation
            correlation = filtered_df['Score'].corr(filtered_df['HelpfulnessRatio'])
            text(f"**Correlation between Rating and Helpfulness:** {correlation:.3f}")
            
            if correlation > 0.3:
                text("**💡 Insight:** There is a positive correlation between ratings and helpfulness, suggesting customers find positive reviews more helpful.")
            elif correlation < -0.3:
                text("**💡 Insight:** There is a negative correlation between ratings and helpfulness, suggesting customers find critical reviews more helpful.")
            else:
                text("**💡 Insight:** There is little correlation between ratings and helpfulness, suggesting customers value both positive and negative reviews.")
        
        # Visualization: Time Trends with enhanced analysis
        if 'Year' in filtered_df.columns and 'Month' in filtered_df.columns:
            text("## 📅 Review Trends Over Time")
            
            try:
                # Improve time grouping with proper sorting
                time_grouped = filtered_df.groupby('YearMonth').agg(
                    count=('Score', 'count'),
                    avg_score=('Score', 'mean')
                ).reset_index()
                
                # Sort by YearMonth
                time_grouped['YearMonth'] = pd.to_datetime(time_grouped['YearMonth'])
                time_grouped = time_grouped.sort_values('YearMonth')
                time_grouped['YearMonth'] = time_grouped['YearMonth'].dt.strftime('%Y-%m')
                
                # Create a dual-axis chart with trendlines
                fig_time = go.Figure()
                
                # Add bars for review count
                fig_time.add_trace(go.Bar(
                    x=time_grouped['YearMonth'],
                    y=time_grouped['count'],
                    name='Number of Reviews',
                    marker_color='#3366CC'
                ))
                
                # Add line for average score
                fig_time.add_trace(go.Scatter(
                    x=time_grouped['YearMonth'],
                    y=time_grouped['avg_score'],
                    name='Average Rating',
                    marker_color='#FF6600',
                    mode='lines+markers',
                    yaxis='y2',
                    line=dict(width=2)
                ))
                
                # Add moving average for the rating trend
                window_size = min(3, len(time_grouped))
                if window_size > 1:
                    time_grouped['moving_avg'] = time_grouped['avg_score'].rolling(window=window_size).mean()
                    
                    fig_time.add_trace(go.Scatter(
                        x=time_grouped['YearMonth'],
                        y=time_grouped['moving_avg'],
                        name=f'{window_size}-Month Moving Average',
                        line=dict(color='#FF0000', width=2, dash='dash'),
                        mode='lines',
                        yaxis='y2'
                    ))
                
                fig_time.update_layout(
                    title='Reviews Over Time with Rating Trend',
                    xaxis=dict(title='Year-Month'),
                    yaxis=dict(title='Number of Reviews', side='left'),
                    yaxis2=dict(
                        title='Average Rating',
                        overlaying='y',
                        side='right',
                        range=[1, 5],
                        showgrid=False
                    ),
                    legend=dict(
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='center',
                        x=0.5
                    ),
                    height=500
                )
                
                plotly(fig_time)
                
                # Add day of week analysis if available
                if 'DayOfWeek' in filtered_df.columns:
                    text("### Review Patterns by Day of Week")
                    
                    # Create day of week mapping
                    day_mapping = {
                        0: 'Monday',
                        1: 'Tuesday',
                        2: 'Wednesday',
                        3: 'Thursday',
                        4: 'Friday',
                        5: 'Saturday',
                        6: 'Sunday'
                    }
                    
                    # Add day names
                    filtered_df['DayName'] = filtered_df['DayOfWeek'].map(day_mapping)
                    
                    # Group by day of week
                    day_grouped = filtered_df.groupby('DayName').agg(
                        count=('Score', 'count'),
                        avg_score=('Score', 'mean')
                    ).reset_index()
                    
                    # Ensure proper day order
                    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    day_grouped['DayOrder'] = day_grouped['DayName'].map(lambda x: day_order.index(x))
                    day_grouped = day_grouped.sort_values('DayOrder')
                    
                    # Create day of week chart
                    fig_day = go.Figure()
                    
                    # Add bars for review count
                    fig_day.add_trace(go.Bar(
                        x=day_grouped['DayName'],
                        y=day_grouped['count'],
                        name='Number of Reviews',
                        marker_color='#3366CC'
                    ))
                    
                    # Add line for average score
                    fig_day.add_trace(go.Scatter(
                        x=day_grouped['DayName'],
                        y=day_grouped['avg_score'],
                        name='Average Rating',
                        marker_color='#FF6600',
                        mode='lines+markers',
                        yaxis='y2',
                        line=dict(width=2)
                    ))
                    
                    fig_day.update_layout(
                        title='Review Patterns by Day of Week',
                        xaxis=dict(title='Day of Week'),
                        yaxis=dict(title='Number of Reviews', side='left'),
                        yaxis2=dict(
                            title='Average Rating',
                            overlaying='y',
                            side='right',
                            range=[1, 5],
                            showgrid=False
                        ),
                        legend=dict(
                            orientation='h',
                            yanchor='bottom',
                            y=1.02,
                            xanchor='center',
                            x=0.5
                        ),
                        height=400
                    )
                    
                    plotly(fig_day)
                    
                    # Add insights
                    busiest_day = day_grouped.loc[day_grouped['count'].idxmax()]['DayName']
                    highest_rated_day = day_grouped.loc[day_grouped['avg_score'].idxmax()]['DayName']
                    
                    text(f"**💡 Insights:** {busiest_day} is the most active day for reviews. {highest_rated_day} has the highest average rating.")
                
                # Add time trend insights
                if len(time_grouped) > 2:
                    # Calculate trend direction using a simple linear regression
                    x = np.arange(len(time_grouped))
                    y = time_grouped['avg_score'].values
                    
                    # Calculate slope using numpy's polyfit
                    slope = np.polyfit(x, y, 1)[0]
                    
                    if slope > 0.05:
                        text("**💡 Insight:** Ratings show a positive trend over time, suggesting improving customer satisfaction.")
                    elif slope < -0.05:
                        text("**💡 Insight:** Ratings show a negative trend over time, suggesting declining customer satisfaction.")
                    else:
                        text("**💡 Insight:** Ratings have remained relatively stable over time.")
                
            except Exception as e:
                text(f"⚠️ Error creating time series chart: {str(e)}")
        
        # Product Analysis with better visualizations
        if 'ProductId' in filtered_df.columns:
            text("## 🛍️ Product Performance Analysis")
            
            try:
                # Group by ProductId and calculate stats
                product_stats = filtered_df.groupby('ProductId').agg(
                    avg_score=('Score', 'mean'),
                    review_count=('Score', 'count')
                ).reset_index()
                
                if 'HelpfulnessRatio' in filtered_df.columns:
                    product_helpfulness = filtered_df.groupby('ProductId')['HelpfulnessRatio'].mean().reset_index()
                    product_stats = product_stats.merge(product_helpfulness, on='ProductId')
                
                # Add sentiment percentages
                sentiment_by_product = filtered_df.groupby('ProductId')['Sentiment'].value_counts().unstack().fillna(0)
                
                # Calculate sentiment percentages
                if all(x in sentiment_by_product.columns for x in ['Positive', 'Neutral', 'Negative']):
                    total_reviews = sentiment_by_product.sum(axis=1)
                    
                    sentiment_by_product['Positive_pct'] = sentiment_by_product['Positive'] / total_reviews * 100
                    sentiment_by_product['Negative_pct'] = sentiment_by_product['Negative'] / total_reviews * 100
                    
                    # Add to product stats
                    sentiment_by_product = sentiment_by_product.reset_index()
                    product_stats = product_stats.merge(
                        sentiment_by_product[['ProductId', 'Positive_pct', 'Negative_pct']], 
                        on='ProductId',
                        how='left'
                    )
                
                # Filter to products with multiple reviews
                min_reviews = max(2, int(filtered_df['ProductId'].value_counts().quantile(0.75)))
                product_stats = product_stats[product_stats['review_count'] >= min_reviews]
                
                # Sort by review count for top products
                top_products = product_stats.sort_values('review_count', ascending=False).head(15)
                
                # Create horizontal bar chart for top products
                fig_top = px.bar(
                    top_products,
                    y='ProductId',
                    x='review_count',
                    orientation='h',
                    color='avg_score',
                    title=f'Top 15 Products by Review Count (Min {min_reviews} reviews)',
                    labels={
                        'ProductId': 'Product ID',
                        'review_count': 'Number of Reviews',
                        'avg_score': 'Average Rating'
                    },
                    color_continuous_scale='Viridis',
                    text='avg_score'
                )
                
                fig_top.update_traces(
                    texttemplate='%{text:.2f}',
                    textposition='outside'
                )
                
                fig_top.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    height=600,
                    margin=dict(l=150)  # Add more space for product IDs
                )
                
                plotly(fig_top)
                
                # Create scatter plot with improved visuals
                text("### Product Rating vs. Review Volume")
                
                # Determine marker size range based on data
                min_reviews = product_stats['review_count'].min()
                max_reviews = product_stats['review_count'].max()
                
                # Create a scatter plot that shows the relationship between reviews and ratings
                fig_scatter = px.scatter(
                    product_stats,
                    x='review_count',
                    y='avg_score',
                    size='review_count',
                    color='HelpfulnessRatio' if 'HelpfulnessRatio' in product_stats.columns else 'avg_score',
                    hover_name='ProductId',
                    size_max=50,
                    title='Product Performance Matrix: Rating vs. Popularity',
                    labels={
                        'review_count': 'Number of Reviews (Popularity)',
                        'avg_score': 'Average Rating (Quality)',
                        'HelpfulnessRatio': 'Helpfulness Ratio'
                    },
                    color_continuous_scale='Viridis'
                )
                
                # Add quadrant separators for analysis
                median_reviews = product_stats['review_count'].median()
                median_score = product_stats['avg_score'].median()
                
                fig_scatter.add_shape(
                    type="line",
                    x0=median_reviews,
                    y0=1,
                    x1=median_reviews,
                    y1=5,
                    line=dict(color="Red", width=1, dash="dash")
                )
                
                fig_scatter.add_shape(
                    type="line",
                    x0=0,
                    y0=median_score,
                    x1=max_reviews * 1.1,
                    y1=median_score,
                    line=dict(color="Red", width=1, dash="dash")
                )
                
                # Add quadrant labels
                fig_scatter.add_annotation(
                    x=median_reviews/2,
                    y=median_score + (5 - median_score)/2,
                    text="High Quality<br>Low Popularity",
                    showarrow=False,
                    font=dict(size=10)
                )
                
                fig_scatter.add_annotation(
                    x=median_reviews + (max_reviews - median_reviews)/2,
                    y=median_score + (5 - median_score)/2,
                    text="Star Products<br>High Quality & Popularity",
                    showarrow=False,
                    font=dict(size=10)
                )
                
                fig_scatter.add_annotation(
                    x=median_reviews/2,
                    y=median_score/2,
                    text="Problematic Products<br>Low Quality & Popularity",
                    showarrow=False,
                    font=dict(size=10)
                )
                
                fig_scatter.add_annotation(
                    x=median_reviews + (max_reviews - median_reviews)/2,
                    y=median_score/2,
                    text="Improvement Needed<br>High Popularity, Low Quality",
                    showarrow=False,
                    font=dict(size=10)
                )
                
                fig_scatter.update_layout(
                    height=600,
                    xaxis=dict(
                        title='Number of Reviews (Popularity)',
                        type='log' if max_reviews / min_reviews > 100 else 'linear'
                    )
                )
                
                plotly(fig_scatter)
                
                # Add insights
                top_rated_product = product_stats.sort_values('avg_score', ascending=False).head(1)
                top_rated = top_rated_product['ProductId'].values[0]
                top_rated_score = top_rated_product['avg_score'].values[0]
                
                most_reviewed_product = product_stats.sort_values('review_count', ascending=False).head(1)
                most_reviewed = most_reviewed_product['ProductId'].values[0]
                most_reviewed_count = most_reviewed_product['review_count'].values[0]
                
                text(f"**Top Products:**")
                text(f"- Highest Rated: {top_rated} with {top_rated_score:.2f} average rating")
                text(f"- Most Reviewed: {most_reviewed} with {most_reviewed_count:,} reviews")
                
                # Display top products table
                text("### Detailed Product Statistics")
                product_display = product_stats.sort_values('review_count', ascending=False).head(10)
                
                # Rename columns for better readability
                display_cols = {
                    'ProductId': 'Product ID',
                    'avg_score': 'Average Rating',
                    'review_count': 'Number of Reviews'
                }
                
                if 'HelpfulnessRatio' in product_display.columns:
                    display_cols['HelpfulnessRatio'] = 'Helpfulness Ratio'
                
                if 'Positive_pct' in product_display.columns:
                    display_cols['Positive_pct'] = 'Positive Reviews (%)'
                    display_cols['Negative_pct'] = 'Negative Reviews (%)'
                
                product_display = product_display.rename(columns=display_cols)
                
                # Format percentages
                if 'Positive Reviews (%)' in product_display.columns:
                    product_display['Positive Reviews (%)'] = product_display['Positive Reviews (%)'].round(1)
                    product_display['Negative Reviews (%)'] = product_display['Negative Reviews (%)'].round(1)
                
                table(product_display, title="Top 10 Products by Review Count")
                
            except Exception as e:
                text(f"⚠️ Error creating product analysis: {str(e)}")
    
    else:
        text("⚠️ Cannot create visualizations because the required columns are missing.")