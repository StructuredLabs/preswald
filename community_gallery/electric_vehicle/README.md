# Electric Vehicle Dashboard

## Overview
This project provides an interactive dashboard to analyze electric vehicle data. The dashboard offers insights into vehicle models, electric ranges, and other key attributes using data visualization and interactive components.

## Features
- **Data Filtering**: View electric vehicles from 2015 onwards, sorted by electric range.
- **Interactive Slider**: Dynamically filter data by model year.
- **Scatter Plot Visualization**: Compare electric range by model year with a color-coded manufacturer distinction.
- **SQL Query Integration**: Retrieve and display specific data using a query-based approach.

## Setup
1. **Install Dependencies**
   Ensure you have all necessary Python packages installed:
   ```sh
   pip install pandas plotly preswald
   ```

2. **Configure Data Connections**
   - Modify `preswald.toml` to define data sources.
   - Store sensitive credentials (API keys, database passwords) in `secrets.toml`.

3. **Run the Application**
   Execute the following command to start the dashboard:
   ```sh
   preswald run 
   ```

## Usage
- Adjust the **Model Year Threshold** slider to filter data dynamically.
- Analyze the **Filtered Data Table** to see the most relevant vehicle information.
- Explore the **Scatter Plot** for insights on electric range distribution across years.

## Acknowledgments
Built with [Preswald](https://preswald.com) for interactive data visualization.

