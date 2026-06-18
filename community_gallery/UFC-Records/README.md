# MMA Fighter Records App

## Overview
This is an example Preswald app that loads, filters, and visualizes MMA fighter records data from a CSV file. The app demonstrates how to:
- Load data using Preswald.
- Filter records by a specific category (e.g., "Total Fights").
- Dynamically filter records based on a "Total" value using a slider.
- Visualize data with a scatter plot (Rank vs Total).

## Dataset
The dataset is stored in `data/UFC_Records.csv` and contains records for MMA fighters with the following columns:
- **Type of Record:** The category of record (e.g., "Total Fights", "Wins").
- **Rank:** The fighter's rank within the category.
- **Name:** The fighter's name.
- **Total:** A numerical value representing a specific metric (e.g., total fights, wins).

## What the App Does
- **Data Loading:**  
  Loads the CSV dataset defined in `preswald.toml` using the key `sample_csv`.
  
- **Filtering:**  
  Filters the data to display only records where the "Type of Record" is "Total Fights". A slider allows users to filter fighters based on a minimum "Total" value.
  
- **Visualization:**  
  Creates a scatter plot that displays the relationship between a fighter's rank and their total value, with fighter names shown on hover.

## How to Run
1. **Setup Your Environment:**
   - Install Preswald:
     ```bash
     pip install preswald
     ```
   - Ensure the dataset (`UFC_Records.csv`) is located in the `data/` folder and referenced correctly in the `preswald.toml` file.

2. **Run Locally:**
   In your project directory, run:
   ```bash
   preswald run
