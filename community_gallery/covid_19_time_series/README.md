# 📌 US COVID-19 Cases & Deaths Over Time 📌
This project visualizes cumulative COVID-19 confirmed cases & deaths across the United States over time. It provides an interactive bubble map to track the progression of the pandemic, along with a dynamic data table.

## 📂 Dataset Source  
The dataset is sourced from **[Johns Hopkins University COVID-19 Time Series Data](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series)**. It contains daily cumulative confirmed cases and deaths recorded across different US locations.

## 🚀 Features  
- 🌍 **Interactive Bubble Map**: Visualizes COVID-19 cases and deaths geographically on a US map.  
- 📅 **Date Slider**: Allows users to select a date and see COVID-19 data for that day.  
- 🏥 **Color-Coded Severity Levels**: Cases and deaths are grouped into categories, represented by different bubble colors.  
- 📄 **Dynamic Data Table**: Displays both confirmed cases and deaths for each location.  
- ⚡ **Powered by Preswald**: Simple and fast deployment with `preswald`.

## 🛠️ Setup & Running the App

### 1️⃣ Install Dependencies  
Ensure you have `preswald` installed:

```bash
pip install preswald
```
### 2️⃣ Configure Data Sources
Place the COVID-19 dataset files (time series for confirmed cases and deaths) in your project directory.
Define your data connections in preswald.toml.
Store sensitive information (API keys, passwords) in secrets.toml.
### 3️⃣ Run the App
Execute the following command to start the visualization:

```bash
preswald run
```
