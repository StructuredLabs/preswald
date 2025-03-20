# Preswald Take Home Assignment - Meteor Crashes
dataset: https://data.nasa.gov/Space-Science/Meteorite-Landings/gh4g-9sfh/about_data

# Features
The Preswald application provides an interactive dashboard for Viewing and Analyzing Meteorite Crash data for the past 200 years.
- Filtering: A slider component lets users select a threshold for “Data Value.” As they move the slider, the data table updates instantly. The table provides key detail information such as meteor name, crash date, geographical location, classification and its mass.
- Ranging:   The app also allows user to input ranges for the dates between which they want to see meteorite crashes.
- Visualizations: The app uses Plotly to create Pie Chart that helps visualize the distribution of meteor classes over the number of crashes and Maps allows users to visualize different crash site Hovering over data points reveals extra details, providing a deeper look at the dataset.

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run ` to run locally.
