# Indian Startup Funding Analysis 

## Project Overview
This Preswald example does interactive analytics on Indian startup funding data. The dashboard allows users to explore startup investments by funding amount, geography, and industry vertical, offering valuable insights into India's vibrant startup ecosystem.

## Dataset Access
https://www.kaggle.com/datasets/sudalairajkumar/indian-startup-funding


## Features
- **Funding Range Filter**: Slide to select specific funding thresholds and discover startups within your target investment range
- **City-based Analysis**: Filter startups by location to focus on specific regional ecosystems
- **Comprehensive Visualizations**:
  - Year-over-year funding trends via line charts
  - Top 10 funding cities with horizontal bar charts
  - Most active investors ranked by total funding amount
  - Industry distribution through an interactive pie chart

## Data Processing
The application performs several important data cleaning operations:
- Drops rows with missing dates or funding amounts
- Converts funding values from string format to float (Amount in USD column specifically)
- Extracts year and month from date strings
- Handles outliers by using percentile ranges for filtering

## Setup Instructions

### Prerequisites
- Python 3.7+
- Preswald library

### Installation
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Ensure you have the required Python packages:
   ```
   pip install preswald pandas numpy plotly
   ```

### Running the Application
```bash
preswald run app.py
```

## Data Source
The application uses the "indian_startup_funding" dataset, which contains information such as:
- Startup names
- Funding amounts in USD
- Funding dates
- Industry verticals
- Investor information
- City locations

## Future Enhancements
Potential improvements for future versions:
- Implement investor-specific analytics
- Create geographical heatmap of funding distribution, state wise on the Indian map?
- Include funding round type analysis (Seed, Series A, B, etc.)
