# IPL 2024 Auction Data Dashboard

## Overview
This Preswald application provides an interactive dashboard for exploring IPL 2024 Auction data.
Deployed link : https://ipl-2024-auction-111794-eeuhhhoq.preswald.app
## Features
- Interactive Filtering: A slider component lets users select a threshold for "Price Paid." As they move the slider, the visualizations update instantly.
- Data Analysis: The dashboard provides insights into player nationalities, price distributions, and roles.
- Visualizations: The app uses Plotly to create pie charts, histograms, and strip plots. Hovering over data points reveals extra details about players and their auction prices. 

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run` to run locally

## Data Source
The data used is from the IPL 2024 Auction, containing information about player prices, nationalities, and roles.
dataset : https://www.kaggle.com/datasets/sandeepmistry2004/ipl-2024-players-auction-stats

