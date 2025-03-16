# Mobile Data Dashboard

A dashboard to visualize mobile data till 2025, providing actionable insights and showcasing various components offered by Preswald.

## Dataset Source

The dataset used in this project is sourced from Kaggle:  
[Mobiles Dataset 2025](https://www.kaggle.com/datasets/abdulmalik1518/mobiles-dataset-2025).  
It contains information about mobile phone models, their launch years, prices across different regions, battery capacities, and other specifications.

## Features

- **Top 10 Brands by Number of Models**: Visualizes the most active mobile brands in terms of model launches.
- **Brand Market Share**: Displays the market share of different brands based on the number of models launched.
- **Models Launched Per Year**: Tracks the number of mobile models released each year.
- **Dynamic Price vs Battery Capacity Comparison**: Allows users to analyze price trends based on battery capacity.
- **Average Launch Price by Region**: Displays the average phone prices for different regions.
- **Search Phone Prices**: Users can search for specific phone models and view their prices.
- **Full Dataset View**: Shows the entire dataset for reference.

## How to Run

1. **Clone the repository**  

2. **Setup**
 - Configure your data connections in `preswald.toml`
 - Add sensitive information (passwords, API keys) to `secrets.toml`
 - Run your app with `preswald run` locally.