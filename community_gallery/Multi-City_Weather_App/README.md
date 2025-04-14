# Multi-City Weather Comparison Dashboard

## 📌 Overview

The Multi-City Weather Comparison Dashboard is an interactive web application built using Preswald and Plotly to visualize and compare weather metrics across multiple cities. Users can select cities from a dropdown, filter data based on temperature thresholds, and explore various weather parameters, including temperature, humidity, wind speed, and precipitation.

## 📂 Dataset Source

The dataset used in this project is multi_city_weather.csv, sourced from https://www.kaggle.com/datasets/bhargavyagnik99/weather-100-top-10-cities-of-10-countries-july which contains weather data for various cities worldwide. The data includes:

- City
- Temperature (Min, Max, Avg)
- Humidity (Avg)
- Wind Speed (Avg)
- Precipitation

The dataset was curated to provide meaningful insights into weather trends across different regions. For performance and clarity, only five cities are included:

- 🇺🇸 New York, Los Angeles (USA)
- 🇮🇳 Delhi, Mumbai (India)
- 🇨🇦 Toronto (Canada)

## 🚀 Features

**🔍 Searchable City Selection**

- Users can select two cities from the dropdown and compare their weather data side by side.

**🌡 Temperature Threshold Filtering**

- A slider allows users to filter data above a certain temperature threshold.
- This helps in analyzing hot and cold trends in selected cities.

**📊 Data Visualizations**

- The app includes interactive charts powered by Plotly:
- Temperature Comparison (Bar Chart)
- Humidity Levels (Scatter Plot)
- Wind Speed Analysis (Line Chart)
- Precipitation Trends (Bar Chart)
- Overall Weather Variation (Multi-factor Scatter Plot)

**📃 Dynamic Table View**

- The table only displays relevant weather columns for selected cities, ensuring a clean UI.
- Dynamic filtering based on temperature threshold.

## Local Setup

**Ensure you have Preswald CLI installed. If not, install it using:**

```
pip install preswald
```

**Clone the Repository**

```
git clone https://github.com/Vkpro55/preswald
cd preswald
```

**Access the App**

Once the server starts, navigate to the this directory

```
cd community_gallery\Multi-City_Weather_App
```

**Run server**

```
preswald run
```

## Deploy on Structured Cloud

**Get the API Key**

- Go to https://app.preswald.com
- Create new organization
- Navigate to setting -> API Key
- Copy this API Key

**Deploye with single command**

```
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```
