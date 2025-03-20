# Preswald Project

# Analysis of Weather data

## Dataset Source
The dataset used in this app is a weather data CSV file, sourced from [Kaggle](https://www.kaggle.com/datasets/zaraavagyan/weathercsv?resource=download). It contains various meteorological information, including temperature, humidity, wind speed, and weather conditions. The data provides valuable insights into weather patterns and trends.

## What the App Does
This app analyzes and visualizes weather data to help users understand temperature variations and weather conditions over time. It offers the following features:
- **Dynamic Filtering:** Adjust temperature thresholds using a slider.
- **Real-Time Data Display:** View filtered data instantly.
- **Scatter Plot Visualization:** Visualize temperature changes over time.
- **Interactive UI:** Responsive and easy-to-use interface with instant updates.

## How to Run and Deploy It
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-github-username/weather-app.git
   cd weather-app
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app locally:**
   ```bash
   preswald run hello.py
   ```
4. **Access the app:**
   Open your browser and visit:
   ```
   http://localhost:8501
   ```
5. **To deploy the app, use the following command:**
   ```bash
   preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
   ```
   Once deployed, access the live preview link provided by Preswald to view your app.

## Troubleshooting
- **No Data Available:** Check if the dataset file is correctly loaded and located at the specified path.
- **Empty Plot:** Adjust the temperature threshold to include more data points.
- **Deployment Issues:** Verify your API key and GitHub username for correctness.

