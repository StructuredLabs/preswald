# World Happiness Explorer

## Overview
An interactive dashboard to explore global happiness data from the World Happiness Report 2023. Features a map, trend charts, scatter plots, and filters, all wrapped in a modern, user-friendly UI.

## Dataset
- **Source**: [World Happiness Report 2023](https://www.kaggle.com/datasets/ajaypalsinghlo/world-happiness-report-2023)
- **File**: `data/happiness_2023.csv`

## How to Run Locally
1. Ensure Preswald is installed: `pip install preswald`
2. Place `happiness_2023.csv` in the `data/` folder.
3. Run the app: `preswald run`

## How to Deploy
1. Deploy to Structured Cloud: `preswald deploy --target structured --github <your-username> --api-key <your-api-key> hello.py`
2. Verify the app is live and accessible.

## Features
- Interactive choropleth map of happiness scores by country
- Line chart for happiness trends over time
- Scatter plot for factor correlations
- Filters for countries, years, and factors
- Responsive, styled UI with real-time feedback