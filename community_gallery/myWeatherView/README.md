# MyWeatherView

## Description
MyWeatherView is a weather visualization app that allows users to view and compare weather trends for a selected city over the years. Users can select specific years they want to compare, providing a customizable and insightful experience.

## Dataset Source
The dataset used in this project is sourced from [Kaggle](https://www.kaggle.com/datasets/balabaskar/historical-weather-data-of-all-country-capitals). It contains historical weather data for the capitals of 194 countries. However, to deploy the app efficiently, we have reduced the dataset size to include data for only one country. Future updates will aim to restore the full dataset and enhance functionality.

## Features
- Visualize weather trends for a single city.
- Compare weather data across user-selected years.

## Setup
1. Configure your data connections in `preswald.toml`.
2. Add sensitive information (passwords, API keys) to `secrets.toml`.

## Deployment
1. To deploy run command:
    "preswald deploy --target structured --github <github_username> --api-key <your_API_KEY> hello.py 