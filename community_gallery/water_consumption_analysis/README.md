# Water Data Analysis Project

## Setup
1. Configure  data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`

## 📄 About Dataset
Water is one of the most critical resources for human survival, yet global water consumption is increasing at an alarming rate. This dataset provides a comprehensive analysis of water usage trends across different countries from 2000 to 2024, helping researchers, policymakers, and data analysts understand water consumption patterns, scarcity levels, and sector-wise distribution.

## 🔥 Why This Dataset?
- Covers 25+ years of global water consumption trends
- Includes sector-wise distribution (Agriculture, Industry, Household)
- Tracks water scarcity levels and groundwater depletion
- Useful for data visualization, forecasting, and machine learning applications

Link: [Water Data](https://www.kaggle.com/datasets/atharvasoundankar/global-water-consumption-dataset-2000-2024/data)

## This application allows you to interactively navigate water usage statistics

- **Loads Data:** Loads data on water consumption from a CSV file.
- **Shows Statistics:** Presents numbers aggregated like mean and max per capita water consumption.
- **Interactive Filtering:** Allows you to filter the data by water usage and by year using sliders.
- **Data Tables:** Displays both SQL-filtered and dynamically filtered data in tables.
- **Scatter Plot:** Graphs total water consumption vs. impact of rainfall with points colored according to level of water scarcity.
- **Stacked Bar Chart:** Displays mean breakdown of water consumption (household, industry, agriculture) by level of scarcity.