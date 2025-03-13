# 💨 Air Quality Data Explorer

Find the app here- [Air Quality Analyzer](https://hello-preswald-594423-ayz7cig6-ndjz2ws6la-ue.a.run.app/)

## Dataset Source

The dataset used in this project is derived from **New York City Air Quality data**. The data includes various air quality indicators across different geographical areas of NYC, including measurements of pollutants, health impacts, and environmental factors from 2005 to 2022. This comprehensive dataset allows for analysis and visualization of air quality trends across different neighborhoods, boroughs, and time periods.

The dataset used is a CSV file named `Air_Quality.csv`, which includes the following columns:
- **Unique ID**: Unique identifier for each record
- **Indicator ID**: ID associated with the air quality measurement type
- **Name**: Name of the indicator (e.g., Fine particles, Nitrogen dioxide)
- **Measure**: Type of measurement (e.g., Mean, Estimated annual rate)
- **Measure Info**: Unit of measurement (e.g., ppb, mcg/m3)
- **Geo Type Name**: Geographical classification (e.g., UHF42, CD, Borough)
- **Geo Join ID**: Geographical area ID
- **Geo Place Name**: Name of the geographical area
- **Time Period**: Time frame of the measurement
- **Start_Date**: Start date of the measurement period
- **Data Value**: The recorded value of the measurement
- **Message**: Additional information (if any)

Key indicators in the dataset include:
- **Fine particles (PM 2.5)**: Particulate matter measurements
- **Nitrogen dioxide (NO2)**: NO2 concentration levels
- **Ozone (O3)**: Ozone measurement data
- **Boiler Emissions- Total SO2 Emissions**: Sulfur dioxide emission data
- **Asthma emergency department visits**: Health impact data related to air quality
- **Respiratory hospitalizations**: Health impact data related to air quality

The dataset is crucial for exploring air quality variations across NYC and understanding the relationship between air pollutants and health outcomes in different communities.

## What Does the App Do?

The **Air Quality Data Explorer** is an interactive dashboard that visualizes and analyzes air quality data from New York City. The app provides:

- **Dataset Overview**: Displays basic statistics about the dataset, including record count and date range.

- **Metric-by-Metric Analysis**: For key pollutants like Fine particles (PM 2.5), Nitrogen dioxide (NO2), and Ozone (O3), the app provides:
  - Average and maximum values with health interpretation based on EPA standards
  - Time series analysis with trend lines showing year-over-year changes
  - Statistical indicators of increasing or decreasing pollutant levels
  - Geographic comparison showing the most recent measurements across neighborhoods
  
- **Seasonal Analysis**: When available, shows how air quality varies between summer and winter with:
  - Seasonal trend charts over multiple years
  - Box plots showing distribution of values by season
  - Statistical analysis of the differences between seasons
  
- **Health Implications Assessment**: 
  - Pie charts showing the percentage of measurements falling into different health quality categories
  - Tables highlighting areas with the highest health concerns
  
- **Data Explorer**: An interactive table that allows users to browse the raw data with a configurable number of rows to display.

The app helps users understand air quality patterns in NYC, identify trends over time, observe seasonal variations, and recognize locations with potential health concerns due to poor air quality.

## How to Run the App Locally

### Prerequisites

1. **Install Python**: Ensure you have Python 3.7 or higher installed. You can download Python from [here](https://www.python.org/downloads/).
   
2. **Install Required Packages**: The project relies on the following Python libraries:
   - `pandas` for data manipulation
   - `plotly` for visualizations
   - `preswald` for app functionality
   - `numpy` for numerical operations

   To install the required packages, run the following command in your terminal:
   ```bash
   pip install pandas plotly preswald numpy
   ```

### Running the App

1. **Clone the repository** or download the files.
   
2. **Prepare the Dataset**: Make sure the `Air_Quality.csv` file is in the `data` directory. The data should be properly cleaned, with any missing values handled appropriately.

3. **Run the App**:
   Once all dependencies are installed and your dataset is in place, you can run the app locally by using the following command in your terminal:
   ```bash
   preswald run
   ```

   This will start the app locally, and you can open it in your web browser at the provided local URL.

## How to Deploy the App

### 1. **Deploy Locally with Preswald** (for Development)

   Once you have the app working locally, you can deploy it using **Preswald**'s deployment tools.

   - Make sure you're logged in to Preswald and have the necessary API keys. You can generate an API key by visiting [Preswald's API Keys page](https://app.preswald.com/settings/api-keys).
   
   - Run the following command to deploy the app to **Preswald**:
     ```bash
     preswald deploy --target structured --github --api-key YOUR_API_KEY
     ```

   Replace `YOUR_API_KEY` with your actual Preswald API key.

### 2. **Deployment Steps**:

   - **Create a New Organization**: Go to [Preswald's website](https://app.preswald.com/) and create a new organization.
   - **Generate an API Key**: Navigate to **Settings > API Keys** to generate a new API key.
   - **Deploy**: Use the `preswald deploy` command to deploy your app.

   After deployment, a live preview link will be generated. You can share the link or use it to access the app from any device.

## Additional Notes

- This dataset offers rich opportunities for environmental health analysis, particularly for studying the relationship between air quality and respiratory health outcomes.
- Consider enhancing the app with additional features such as:
  - Predictive modeling for future air quality trends
  - Correlation analysis between different pollutants
  - Demographic overlays to explore environmental justice issues
  - Comparison with EPA air quality standards
- Regular updates to the dataset will ensure the most current air quality information is available for analysis.

---

Explore New York City's air quality patterns and their health impacts through this interactive and informative dashboard!
