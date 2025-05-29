# Aviation Data Visualization Project

## Overview
This project analyzes and visualizes aviation data focused on city-pair markets. The dataset includes information on market connections, passenger counts, average fares, yield (fare per mile), and average travel distances across major cities.

## Demo Video
https://drive.google.com/file/d/1eYr-SLE3I4n_aqZ6mVo4Ufn_QBD19dFG/view?usp=sharing

## Dataset
https://catalog.data.gov/dataset/consumer-airfare-report-table-2-top-1000-city-pair-markets

## Visualizations
The project features several interactive visualizations:

1. **Geographic Scatter Plot** - Displays passenger population across cities on a map
2. **Fare Trend Analysis** - Line graph tracking fare changes over time
3. **3D Relationship Analysis** - Explores the relationship between average flight distances, passenger counts, and fares

## Technologies Used
- Python
- Pandas for data manipulation
- Plotly Express for interactive visualizations
- Preswald for app deployment

## Key Insights
- Identified correlations between flight distance and fare structures
- Analyzed how market connectivity affects passenger volumes
- Discovered pricing anomalies across different city pairs
- Visualized regional differences in aviation metrics

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`
