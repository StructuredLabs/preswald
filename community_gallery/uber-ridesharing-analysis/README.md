# Uber Ridesharing Analysis

## About
This interactive application analyzes NYC Uber trip data from January-February 2015. The app visualizes trip patterns, active vehicles, and other metrics across different bases and time periods.

## Live Demo
Check out the live application here: [Uber Ridesharing Analysis](https://uber-ridesharing-analysis-710557-kx3ia9zr-ndjz2ws6la-ue.a.run.app/)

## Dataset
The application uses Uber trip data stored in CSV format (`data/Uber-Jan-Feb-FOIL.csv`). This dataset contains information about Uber rides in New York City during January and February 2015.

Data source: [Uber Pickups in New York City](https://www.kaggle.com/datasets/fivethirtyeight/uber-pickups-in-new-york-city)

## Features
- Interactive filters for bases and dates
- Visualizations of trip patterns and vehicle utilization
- Analysis of weekday vs weekend trends

## Setup and Running
1. Install the Preswald package:
   ```
   pip install preswald
   ```
2. Run the application:
   ```
   preswald run
   ```

## Deployment
The app can be deployed using the Preswald deployment service:
1. Ensure your `preswald.toml` file has the correct project slug
2. Deploy using the following command:
   ```
   preswald deploy --target structured --github <github-username> --api-key <structured-api-key> hello.py
   ```
3. Your app will be available at the URL provided after deployment