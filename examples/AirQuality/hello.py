from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

# Dashboard title and description
text("# Air Quality Analysis Dashboard")
text("This dashboard provides comprehensive visualizations and analysis of air quality data across different neighborhoods and time periods.")

# Load the Air Quality data
connect()
df = get_df("AirQuality")

# Clean and prepare data
if df is not None:
    # Convert date to datetime
    df['Start_Date'] = pd.to_datetime(df['Start_Date'])
    df['Year'] = df['Start_Date'].dt.year
    df['Month'] = df['Start_Date'].dt.month
    
    # Remove any rows with missing Data Value
    df = df.dropna(subset=['Data Value'])
    
    # Overview information
    text(f"## Dataset Overview")
    text(f"This dataset contains **{df.shape[0]} records** with information on air quality metrics from {df['Year'].min()} to {df['Year'].max()}.")
    
    # Basic statistics summary
    text("### Air Quality Metrics Summary")
    
    summary_stats = df.groupby('Name')['Data Value'].agg(['count', 'mean', 'std', 'min', 'max']).reset_index()
    summary_stats.columns = ['Metric', 'Count', 'Average', 'Std Dev', 'Min', 'Max']
    summary_stats = summary_stats.round(2)
    table(summary_stats)
    
    # Health-based interpretation helper function
    def interpret_air_quality(metric, value):
        if pd.isna(value):
            return "Unknown"
        
        if "Fine particles (PM 2.5)" in metric:
            if value <= 12:
                return "Good (Meets EPA Annual Standard)"
            elif value <= 35:
                return "Moderate (Meets EPA 24hr Standard)"
            else:
                return "Poor (Exceeds EPA Standards)"
        
        elif "Nitrogen dioxide (NO2)" in metric:
            if value <= 53:
                return "Good (Meets EPA Annual Standard)"
            elif value <= 100:
                return "Moderate"
            else:
                return "Poor (Exceeds EPA Standards)"
        
        elif "Ozone (O3)" in metric:
            if value <= 70:
                return "Good (Meets EPA 8hr Standard)"
            else:
                return "Poor (Exceeds EPA Standards)"
        
        return "No standard reference available"
    
    #we'll create multiple sections for key metrics
    main_metrics = ["Fine particles (PM 2.5)", "Nitrogen dioxide (NO2)", "Ozone (O3)"]
    available_metrics = [m for m in main_metrics if m in df['Name'].unique()]
    

    if not available_metrics and len(df['Name'].unique()) > 0:
        available_metrics = [df['Name'].unique()[0]]
    
    for selected_metric in available_metrics:
        # Filter data based on selection
        filtered_df = df[df['Name'] == selected_metric]
        
        # Choose UHF42 if available, otherwise use the first geo type
        geo_types = sorted(filtered_df['Geo Type Name'].unique().tolist())
        selected_geo = "UHF42" if "UHF42" in geo_types else geo_types[0]
        
        geo_filtered = filtered_df[filtered_df['Geo Type Name'] == selected_geo]
        
        # Create analysis sections
        text(f"## {selected_metric} Analysis ({selected_geo})")
        
        # Health implications
        avg_value = geo_filtered['Data Value'].mean()
        max_value = geo_filtered['Data Value'].max()
        health_impact = interpret_air_quality(selected_metric, avg_value)
        
        text(f"**Average Value:** {avg_value:.2f} {filtered_df['Measure Info'].iloc[0] if not pd.isna(filtered_df['Measure Info'].iloc[0]) else ''}")
        text(f"**Maximum Value:** {max_value:.2f} {filtered_df['Measure Info'].iloc[0] if not pd.isna(filtered_df['Measure Info'].iloc[0]) else ''}")
        text(f"**Health Implications:** {health_impact}")
        
        # Time Series Analysis with trend line
        if len(geo_filtered) > 0:
            # Group by year and calculate average
            yearly_avg = geo_filtered.groupby('Year')['Data Value'].agg(['mean', 'std', 'count']).reset_index()
            yearly_avg.columns = ['Year', 'Mean', 'Std', 'Count']
            
            # Calculate year-over-year change
            yearly_avg['YoY Change'] = yearly_avg['Mean'].pct_change() * 100
            yearly_avg['YoY Change'] = yearly_avg['YoY Change'].round(1)
            
            # Create enhanced time series plot
            fig1 = go.Figure()
            
            # Add main line with error bars
            fig1.add_trace(go.Scatter(
                x=yearly_avg['Year'],
                y=yearly_avg['Mean'],
                mode='lines+markers',
                name='Average',
                line=dict(color='royalblue', width=3),
                marker=dict(size=8),
                hovertemplate='Year: %{x}<br>Value: %{y:.2f}<br>Samples: %{text}<extra></extra>',
                text=yearly_avg['Count']
            ))
            
            # Add error bands
            fig1.add_trace(go.Scatter(
                x=yearly_avg['Year'],
                y=yearly_avg['Mean']+yearly_avg['Std'],
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            fig1.add_trace(go.Scatter(
                x=yearly_avg['Year'],
                y=yearly_avg['Mean']-yearly_avg['Std'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(65, 105, 225, 0.2)',
                name='±1 Std Dev',
                hoverinfo='skip'
            ))
            
            # Add annotations for significant changes
            annotations = []
            for i, row in yearly_avg.iterrows():
                if i > 0 and not pd.isna(row['YoY Change']) and abs(row['YoY Change']) >= 10:
                    change_text = f"{row['YoY Change']:+.1f}%"
                    color = 'green' if row['YoY Change'] < 0 else 'red'
                    annotations.append(dict(
                        x=row['Year'],
                        y=row['Mean'],
                        xanchor='center',
                        yanchor='bottom',
                        text=change_text,
                        showarrow=False,
                        font=dict(color=color)
                    ))
            
            # Add trend line using linear regression if enough points
            if len(yearly_avg) >= 3:
                # Fit linear regression
                x = yearly_avg['Year']
                y = yearly_avg['Mean']
                valid_data = ~np.isnan(y)
                if sum(valid_data) >= 2:
                    x_valid = x[valid_data]
                    y_valid = y[valid_data]
                    coeffs = np.polyfit(x_valid, y_valid, 1)
                    line_eq = np.poly1d(coeffs)
                    
                    # Get start and end years with some padding
                    x_range = np.linspace(min(x_valid), max(x_valid), 100)
                    
                    # Calculate trend direction and magnitude
                    trend_direction = "increasing" if coeffs[0] > 0 else "decreasing"
                    annual_change = coeffs[0]
                    
                    fig1.add_trace(go.Scatter(
                        x=x_range,
                        y=line_eq(x_range),
                        mode='lines',
                        line=dict(dash='dash', color='gray'),
                        name=f'Trend ({annual_change:.3f} per year)'
                    ))
                    
                    text(f"**Trend Analysis:** The data shows a {trend_direction} trend with an average change of {annual_change:.3f} units per year.")
            
            fig1.update_layout(
                title=f'Average {selected_metric} Over Time with Trend Analysis',
                xaxis_title='Year',
                yaxis_title=f"Value ({filtered_df['Measure Info'].iloc[0] if not pd.isna(filtered_df['Measure Info'].iloc[0]) else ''})",
                template='plotly_white',
                hovermode='x unified',
                annotations=annotations
            )
            
            plotly(fig1)
            
            # Geographic comparison - improved
            text(f"### Geographic Comparison for {selected_metric}")
            
            # Get top neighborhoods by count
            top_places = geo_filtered['Geo Place Name'].value_counts().head(12).index.tolist()
            place_filtered = geo_filtered[geo_filtered['Geo Place Name'].isin(top_places)]
            
            # For the latest year available for each location
            recent_data = place_filtered.loc[place_filtered.groupby('Geo Place Name')['Start_Date'].idxmax()]
            recent_data = recent_data.sort_values('Data Value', ascending=False)
            
            # Add health assessment to each location
            recent_data['Health Assessment'] = recent_data['Data Value'].apply(
                lambda x: interpret_air_quality(selected_metric, x)
            )
            
            # Create a diverging color scale based on health assessment
            colors = []
            for assessment in recent_data['Health Assessment']:
                if "Good" in assessment:
                    colors.append('green')
                elif "Moderate" in assessment:
                    colors.append('gold')
                else:
                    colors.append('red')
            
            fig2 = px.bar(
                recent_data, 
                x='Geo Place Name', 
                y='Data Value',
                title=f'Most Recent {selected_metric} by Location',
                labels={
                    'Data Value': filtered_df['Measure Info'].iloc[0] if not pd.isna(filtered_df['Measure Info'].iloc[0]) else 'Value',
                    'Geo Place Name': 'Location'
                },
                hover_data=['Year', 'Time Period', 'Health Assessment'],
                text='Data Value',
                color='Health Assessment',
                color_discrete_map={
                    "Good (Meets EPA Annual Standard)": 'green',
                    "Good (Meets EPA 8hr Standard)": 'green',
                    "Moderate (Meets EPA 24hr Standard)": 'gold',
                    "Moderate": 'gold',
                    "Poor (Exceeds EPA Standards)": 'red',
                }
            )
            
            fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig2.update_layout(template='plotly_white', uniformtext_minsize=8, uniformtext_mode='hide')
            plotly(fig2)
            
            # Enhanced seasonal patterns analysis
            if 'Time Period' in geo_filtered.columns and any('Summer' in str(x) for x in geo_filtered['Time Period']):
                text(f"### Seasonal Patterns for {selected_metric}")
                
                # Extract season from Time Period
                def extract_season(time_period):
                    if pd.isna(time_period):
                        return "Unknown"
                    time_period = str(time_period).lower()
                    if 'summer' in time_period:
                        return 'Summer'
                    elif 'winter' in time_period:
                        return 'Winter'
                    elif 'annual' in time_period:
                        return 'Annual Average'
                    else:
                        return 'Other'
                
                geo_filtered['Season'] = geo_filtered['Time Period'].apply(extract_season)
                seasonal_data = geo_filtered[geo_filtered['Season'].isin(['Summer', 'Winter', 'Annual Average'])]
                
                if len(seasonal_data) > 0:
                    # Multi-year seasonal analysis
                    seasonal_stats = seasonal_data.groupby('Season')['Data Value'].agg(['mean', 'std']).reset_index()
                    seasonal_stats.columns = ['Season', 'Average', 'Std Dev']
                    text("**Seasonal Statistics:**")
                    table(seasonal_stats.round(2))
                    
                    # Create seasonal trend plot
                    seasonal_avg = seasonal_data.groupby(['Year', 'Season'])['Data Value'].mean().reset_index()
                    
                    fig3 = px.line(
                        seasonal_avg, 
                        x='Year', 
                        y='Data Value', 
                        color='Season',
                        title=f'Seasonal Patterns of {selected_metric} Over Time',
                        labels={
                            'Data Value': filtered_df['Measure Info'].iloc[0] if not pd.isna(filtered_df['Measure Info'].iloc[0]) else 'Value',
                            'Year': 'Year'
                        },
                        markers=True,
                        line_shape='spline',
                    )
                    
                    # Add annotations for highest seasonal values
                    for season in seasonal_avg['Season'].unique():
                        season_data = seasonal_avg[seasonal_avg['Season'] == season]
                        max_idx = season_data['Data Value'].idxmax()
                        max_year = season_data.loc[max_idx, 'Year']
                        max_val = season_data.loc[max_idx, 'Data Value']
                        
                        fig3.add_annotation(
                            x=max_year,
                            y=max_val,
                            text=f"Peak: {max_val:.1f}",
                            showarrow=True,
                            arrowhead=3,
                            arrowcolor="black",
                            arrowsize=0.5,
                            ax=-30,
                            ay=-30
                        )
                    
                    fig3.update_layout(
                        template='plotly_white',
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    plotly(fig3)
                    
                    # Seasonal comparison box plot
                    fig4 = px.box(
                        seasonal_data,
                        x='Season',
                        y='Data Value',
                        title=f'Distribution of {selected_metric} by Season',
                        labels={
                            'Data Value': filtered_df['Measure Info'].iloc[0] if not pd.isna(filtered_df['Measure Info'].iloc[0]) else 'Value'
                        },
                        color='Season',
                        points='all'
                    )
                    fig4.update_layout(template='plotly_white')
                    plotly(fig4)
                    
                    # Calculate statistical significance of seasonal differences
                    seasons = seasonal_data['Season'].unique()
                    if len(seasons) >= 2 and 'Summer' in seasons and 'Winter' in seasons:
                        summer_data = seasonal_data[seasonal_data['Season'] == 'Summer']['Data Value']
                        winter_data = seasonal_data[seasonal_data['Season'] == 'Winter']['Data Value']
                        
                        summer_mean = summer_data.mean()
                        winter_mean = winter_data.mean()
                        diff = abs(summer_mean - winter_mean)
                        
                        text(f"**Seasonal Difference Analysis**: The average {selected_metric} is "
                             f"{'higher' if summer_mean > winter_mean else 'lower'} in Summer than Winter "
                             f"by {diff:.2f} units ({abs(diff/winter_mean*100):.1f}%).")
    
    # Health implications section
    text("## Health Implications Analysis")
    
    # Select a metric with health standards if available
    health_metrics = ["Fine particles (PM 2.5)", "Nitrogen dioxide (NO2)", "Ozone (O3)"]
    available_health_metrics = [m for m in health_metrics if m in df['Name'].unique()]
    
    if available_health_metrics:
        selected_health_metric = available_health_metrics[0]
        health_df = df[df['Name'] == selected_health_metric]
        
        # Calculate percentage of measurements in each health category
        health_df['Health Assessment'] = health_df['Data Value'].apply(
            lambda x: interpret_air_quality(selected_health_metric, x)
        )
        
        health_counts = health_df['Health Assessment'].value_counts().reset_index()
        health_counts.columns = ['Category', 'Count']
        health_counts['Percentage'] = (health_counts['Count'] / health_counts['Count'].sum() * 100).round(1)
        
        # Create pie chart
        fig_health = px.pie(
            health_counts, 
            values='Count', 
            names='Category',
            title=f'Health Quality Assessment for {selected_health_metric}',
            color='Category',
            color_discrete_map={
                "Good (Meets EPA Annual Standard)": 'green',
                "Good (Meets EPA 8hr Standard)": 'green',
                "Moderate (Meets EPA 24hr Standard)": 'gold',
                "Moderate": 'gold',
                "Poor (Exceeds EPA Standards)": 'red',
            },
            hover_data=['Percentage'],
        )
        
        fig_health.update_traces(textposition='inside', textinfo='percent+label')
        fig_health.update_layout(template='plotly_white')
        plotly(fig_health)
        
        # Show locations with highest health concerns
        if "Poor" in health_df['Health Assessment'].values:
            text("#### Areas with Health Concerns")
            poor_areas = health_df[health_df['Health Assessment'].str.contains("Poor")].groupby('Geo Place Name')['Data Value'].agg(['mean', 'max', 'count']).reset_index()
            poor_areas.columns = ['Location', 'Average Value', 'Maximum Value', 'Number of Poor Readings']
            poor_areas = poor_areas.sort_values('Maximum Value', ascending=False).head(10)
            table(poor_areas.round(2))
    
    # Display filtered data table
    text("## Data Explorer")
    row_count = min(50, len(df))
    num_rows = slider("Number of rows to display", min_val=5, max_val=row_count, default=10)
    table(df.head(num_rows))

else:
    text("⚠️ Could not load Air Quality data. Please check that the dataset path is correct.")
