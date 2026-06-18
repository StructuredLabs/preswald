# 🚀 Meteorite Impact Data Analysis App

## 📌 Overview

This interactive data visualization app is built using **Preswald** and provides insights into meteorite falls and finds across the globe. The dataset includes information such as meteorite names, classifications, masses, years of impact, and geographical locations.

Our app is designed to be **feature-rich and ambitious**, incorporating dynamic filtering, interactive tables, and scatter plots to explore meteorite impact data in depth.

## 🛠 Features

- **Dynamic Filtering**: Users can interactively filter the dataset based on mass, year of impact, and meteorite type.
- **Interactive Data Table**: A paginated table displaying relevant meteorite data.
- **Geospatial Visualization**: Meteorite impact locations plotted on a world map.
- **Mass vs. Year Analysis**: An interactive scatter plot to analyze trends in meteorite falls over time.

## ⚠ Important Notice: **Loading Takes Time** 

Since we aimed for a **highly detailed and interactive application**, **loading the dataset and rendering visualizations can take time**. 

### **What to Expect?**
1. The site might appear **fully loaded** while it is actually still processing the dataset.
2. **Give it some time** – the data is being fetched, filtered, and visualized dynamically.
3. If the app appears blank or unresponsive at first, **wait at least 30–60 seconds** for full interactivity.

## 📊 Dataset Information

The dataset used in this project is **NASA's Meteorite Landings dataset**, which contains:
- **Name** of the meteorite
- **ID** and classification type
- **Mass** (in grams)
- **Fall status** (Fell vs. Found)
- **Year** of impact
- **Latitude & Longitude** for geospatial analysis

## 📍 How It Works

1. **Data Loading**: The app initializes by connecting to `preswald.toml` and fetching the dataset (`sample_csv`).
2. **Filtering & Querying**:
   - Users can set a **minimum meteorite mass** to filter the dataset dynamically.
   - Data is queried from the dataset in real-time.
3. **Visualizations**:
   - A **scatter plot** of mass vs. year to analyze trends.
   - A **world map** plotting meteorite impact locations.
4. **User Interactions**:
   - Sliders to adjust filtering criteria.
   - Clickable tables with sortable columns.

## 🚀 Deployment & Usage
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`