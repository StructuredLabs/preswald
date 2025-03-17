# Weather Data Visualization - Temperature vs. Wind Speed

## Overview
This project visualizes the relationship between **maximum temperature** and **wind speed** using a historical weather dataset. The application is built with **Preswald**, utilizing **Plotly** for interactive data visualization.

**Live Demo**: [Deployed Project](https://preswald-project-375943-btuqq5ps-ndjz2ws6la-ue.a.run.app/)  

## Dataset
The dataset contains daily weather records from January 2012 to 2015. It includes the following columns:

- **date** - Date of the weather record  
- **precipitation** - Amount of rainfall or snowfall (mm)  
- **temp_max** - Maximum temperature of the day (°C)  
- **temp_min** - Minimum temperature of the day (°C)  
- **wind** - Wind speed (m/s)  
- **weather** - Weather condition (e.g., Rain, Snow, Sun, Drizzle)  

**Link to Dataset**: [Kaggle - WEATHER PREDICTION](https://www.kaggle.com/datasets/ananthr1/weather-prediction)

## Features
- **Scatter Plot Visualization** of maximum temperature vs. wind speed  
- **Interactive elements** with hover effects using Plotly  
- **Color-coded markers** based on weather conditions  

## How to Run

1. **Clone the repository**  
   ```sh
   git clone https://github.com/anshul439/preswald.git
   cd preswald/community_gallery/weather_sample

2. **Install dependencies**
   pip install preswald

3. **Setup**
 - Configure your data connections in `preswald.toml`
 - Run your app with `preswald run` locally.

## **Deploy the App**  
   Run the following command in your terminal:

   ```sh
   preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
   ```

   Replace `<your-github-username>` and `<structured-api-key>` with your credentials.
