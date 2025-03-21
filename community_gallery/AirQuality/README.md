# Preswald Project - Airquality
dataset: https://catalog.data.gov/dataset/air-quality

# Features
The Preswald application provides an interactive dashboard for exploring air quality and emissions data.
- Filtering: A slider component lets users select a threshold for “Data Value.” As they move the slider, the data table updates instantly.
- Queries:   Preswald’s query() function can also filter rows by SQL-like conditions
- Visualizations: The app uses Plotly to create scatter or bar charts. Hovering over data points reveals extra details, providing a deeper look at the dataset.
## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run ` to run locally.
