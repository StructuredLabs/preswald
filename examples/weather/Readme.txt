# Preswald Project
# Weather Data Analysis App

## Dataset Source
The dataset used in this app is a weather data CSV file, sourced from https://www.kaggle.com/datasets/zaraavagyan/weathercsv?resource=download. It contains various meteorological information, including rainfall, temperature, and predictions for whether it will rain tomorrow.

## What the App Does
This app analyzes and visualizes weather data, specifically focusing on rainfall distribution and predicting whether it will rain tomorrow. It offers dynamic filtering of the data based on user input and displays various visualizations like histograms and scatter plots to understand the trends.

## How to Run and Deploy It
1. Clone the repository:
   ```bash
   git clone https://github.com/palankigreeshma1109/preswald.git
2. Install dependencies:
pip install -r requirements.txt
3. Run the app locally:
python hello.py
4. To deploy the app, use the following command:
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
Once deployed, access the live preview link provided by Preswald to view your app.

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`
