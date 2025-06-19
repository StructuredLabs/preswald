#!/usr/bin/env python3
"""
AI-Powered Dashboard Demo for Preswald
=====================================

@author: Topgyal Gurung
@created: 2025-06-12
@description: Demonstrates two new dashboard features I built for Preswald:
              1. Smart Insights Dashboard - automatically analyzes data using AI
              2. Live Data Dashboard - real-time streaming data visualization
              Built with React, Plotly, and OpenAI integration.
"""

import json
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from preswald import (
    live_dashboard,
    markdown,
    separator,
    smart_insights,
    text
)

def generate_sample_data():
    """Generate realistic sample data for testing.
    
    Returns:
        pd.DataFrame: DataFrame containing business metrics with seasonal patterns.
    """
    np.random.seed(42)
    
    # Generate time series data over 100 days
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    
    # Create realistic business metrics with some patterns
    base_sales = 1000
    sales = []
    revenue = []
    users = []
    satisfaction = []
    
    for i, date in enumerate(dates):
        # Add seasonal patterns and trends
        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * i / 30)
        trend_factor = 1 + 0.002 * i
        noise = np.random.normal(0, 0.1)
        
        daily_sales = (base_sales * seasonal_factor * 
                      trend_factor * (1 + noise))
        daily_revenue = daily_sales * (50 + np.random.normal(0, 5))
        daily_users = int(daily_sales * 0.8 + np.random.normal(0, 50))
        daily_satisfaction = min(100, max(0, 85 + np.random.normal(0, 10)))
        
        sales.append(daily_sales)
        revenue.append(daily_revenue)
        users.append(max(0, daily_users))
        satisfaction.append(daily_satisfaction)
    
    return pd.DataFrame({
        'date': dates,
        'sales': sales,
        'revenue': revenue,
        'users': users,
        'satisfaction_score': satisfaction,
        'conversion_rate': np.random.uniform(0.02, 0.08, len(dates)),
        'category': np.random.choice(
            ['Premium', 'Standard', 'Basic'], 
            len(dates)
        )
    })

def create_product_analytics_data():
    """Create product analytics dataset.
    
    Returns:
        pd.DataFrame: DataFrame containing product performance data.
    """
    products = [
        'iPhone 15', 'Galaxy S24', 'Pixel 8', 
        'MacBook Pro', 'Surface Laptop'
    ]
    regions = [
        'North America', 'Europe', 
        'Asia Pacific', 'Latin America'
    ]
    
    data = []
    for product in products:
        for region in regions:
            for month in range(1, 13):
                data.append({
                    'product': product,
                    'region': region,
                    'month': month,
                    'units_sold': random.randint(1000, 10000),
                    'revenue': random.randint(50000, 500000),
                    'customer_rating': round(random.uniform(3.5, 4.9), 1),
                    'return_rate': round(random.uniform(0.01, 0.15), 3),
                    'marketing_spend': random.randint(5000, 50000),
                    'profit_margin': round(random.uniform(0.15, 0.45), 2)
                })
    
    return pd.DataFrame(data)

def main():
    """Main demo application."""
    
    # Header
    markdown("""
    # AI-Powered Analytics Dashboard Demo
    
    This demo shows two new dashboard components I built for Preswald:
    
    ## Features:
    - **Smart AI Analysis** - Automatically analyzes datasets using OpenAI
    - **Real-time Streaming** - Live data updates with animated charts  
    - **Modern UI** - Clean, responsive dashboard design
    - **Interactive Controls** - Start/stop streaming, refresh data, export options
    """)
    
    separator()
    
    # Generate sample datasets
    business_data = generate_sample_data()
    product_data = create_product_analytics_data()
    
    # Convert to format expected by widgets
    business_records = business_data.to_dict('records')
    product_records = product_data.to_dict('records')
    
    # Smart Insights Dashboard
    markdown("""
    ## Smart Insights Dashboard
    
    This widget automatically analyzes your data and generates insights using AI. 
    It looks at patterns, identifies trends, and suggests visualizations.
    """)
    
    smart_insights(
        data=business_records,
        title="Business Performance Analysis",
        id="business_insights"
    )
    
    separator()
    
    # Second example with product data
    smart_insights(
        data=product_records,
        title="Product Analytics Intelligence",
        id="product_insights"
    )
    
    separator()
    
    # Live Data Dashboard
    markdown("""
    ## Live Data Streaming Dashboard
    
    This dashboard shows real-time data updates with animated charts. 
    You can pause/resume the streaming and adjust the update frequency.
    """)
    
    live_dashboard(
        title="Live Operations Dashboard",
        updateInterval=800,  # Update every 800ms
        maxDataPoints=60,    # Keep 1 minute of data
        metrics=['sales', 'users', 'revenue', 'performance'],
        id="live_ops_dashboard"
    )
    
    separator()
    
    # Technical details
    markdown("""
    ## Technical Implementation
    
    ### Smart Insights Dashboard
    - Uses OpenAI API to analyze data and generate insights
    - Automatically calculates basic statistics and data types
    - Generates visualization recommendations based on data structure
    - Handles large datasets efficiently with data sampling
    
    ### Live Data Dashboard  
    - Real-time data streaming with configurable update intervals
    - Smooth animations using Plotly.js transitions
    - Connection status monitoring and error handling
    - Memory-efficient data management (keeps only recent points)
    
    ### Tech Stack
    - **Frontend**: React 18, Plotly.js, Tailwind CSS, Radix UI
    - **Backend**: Python, Pandas, NumPy
    - **AI Integration**: OpenAI GPT models
    - **Performance**: Optimized for real-time updates and large datasets
    
    ### Usage Notes
    - Set your OpenAI API key in the chat widget settings for AI features
    - Live dashboard generates synthetic data for demo purposes
    - Both widgets are fully responsive and work on mobile devices
    - Data can be exported from the visualization widgets
    
    Feel free to experiment with different datasets and settings!
    """)

if __name__ == "__main__":
    main() 