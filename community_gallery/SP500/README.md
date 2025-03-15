# Temperature vs. Humidity Analysis 🌡️💧

This project visualizes the relationship between temperature and humidity using an interactive scatter plot. It helps analyze how humidity changes with temperature across different locations.

## 📂 Dataset Source

The dataset is sourced from [Kaggle's Weather Data](https://www.kaggle.com/datasets/prasad22/weather-data). It contains temperature (°C) and humidity (%) readings collected from various locations.

## 🚀 Features

- 📊 **Interactive Scatter Plot**: Visualizes Temperature vs. Humidity with location labels.
- 📄 **Data Table**: Displays raw dataset values.
- ⚡ **Powered by Preswald**: Simple and fast deployment with `preswald`.

## 🛠️ Setup & Running the App

### 1️⃣ Install Dependencies

Ensure you have `preswald` installed:

```bash
pip install preswald
```

2️⃣ Configure Data Sources

Define your data connections in preswald.toml.
Store sensitive information (API keys, passwords) in secrets.toml.

3️⃣ Run the App
Execute the following command to start the app:

```bash
preswald run hello.py
```

4️⃣ Deploying
To deploy, use:

```bash
preswald deploy
```
