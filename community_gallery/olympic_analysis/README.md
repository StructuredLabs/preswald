# Olympic Games Analysis Dashboard

An interactive dashboard for analyzing Olympic Games performance data across different countries and sports. This example demonstrates how to create a multi-view dashboard with interactive controls and data visualization using Preswald.

## Features

- 🏅 Medal distribution visualization by country
- 📈 Performance trends by sport over time
- 🔄 Interactive year and sport selection
- 📊 Athletes vs medals correlation analysis
- 🗃️ Detailed data table view

## Dataset

The example uses an Olympic Games dataset containing:
- Medal counts (Gold, Silver, Bronze)
- Number of athletes
- Sport categories
- Country participation
- Data for multiple Olympic years (2016, 2020)

## Running the App

1. Install Preswald:
```bash
pip install preswald
```

2. Navigate to the olympic_analysis directory:
```bash
cd community_gallery/olympic_analysis
```

3. Run the app:
```bash
preswald run
```

4. Open your browser and visit: `http://localhost:8501`

## Deploying the App

To deploy the app to Preswald Cloud:

1. Get your API key from [app.preswald.com](https://app.preswald.com)

2. Deploy using:
```bash
preswald deploy --target structured
```

## Learning Points

This example demonstrates:
- Loading and processing structured CSV data
- Creating interactive visualizations with Plotly
- Using Preswald's UI components (select, text, table)
- Building a multi-view dashboard
- Implementing dynamic data filtering
- Working with time-series Olympic data
- Creating stacked bar charts for medal counts
- Analyzing correlations between variables 