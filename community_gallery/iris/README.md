# Iris Data Analysis App

An interactive web application built with Preswald for analyzing the famous Iris dataset.

## Dataset

This application uses the famous [Iris Dataset](https://archive.ics.uci.edu/ml/datasets/iris), a classic dataset in machine learning and statistics. The dataset contains measurements for 150 iris flowers from three different species:
- Setosa
- Versicolor
- Virginica

Each flower has four measurements:
- Sepal length (cm)
- Sepal width (cm)
- Petal length (cm)
- Petal width (cm)

## Features

The application provides:
1. Interactive data filtering using a slider to filter flowers by sepal length
2. Dynamic data table that updates based on the filter
3. Interactive scatter plot visualization showing the relationship between sepal length and width
4. SQL query functionality demonstrating data filtering capabilities


## Project Structure

```
project/
├── data/
│   └── iris.csv      # Iris dataset
├── hello.py          # Main application code
├── preswald.toml     # Preswald configuration
```

## Quick Setup Guide

1. Configure your data connections in `preswald.toml`:
   ```toml
   [data.iris_csv]
   type = "csv"
   path = "data/iris.csv"
   ```

2. Add sensitive information (passwords, API keys) to `secrets.toml`:
   ```toml
   # Example:
   # API_KEY = "your-api-key-here"
   # DB_PASSWORD = "your-database-password"
   ```

3. Run your app:
   ```bash
   preswald run
   ```