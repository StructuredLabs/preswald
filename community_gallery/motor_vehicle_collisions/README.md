# Iris Dataset Explorer

An interactive Preswald app to explore the famous Iris dataset.

## Dataset Source

The Iris dataset is a classic dataset in machine learning and statistics. It contains measurements of 150 iris flowers from three different species: Setosa, Versicolor, and Virginica. The dataset includes four features measured for each sample: sepal length, sepal width, petal length, and petal width (all in centimeters).

The dataset was sourced from the [Seaborn data repository](https://github.com/mwaskom/seaborn-data).

## App Features

This app allows users to:

- Filter data by species
- Select different features for X and Y axes
- Add trend lines to visualize relationships
- View the raw data in a table format

## How to Run

1. Install Preswald:
   ```
   pip install preswald
   ```

2. Clone this repository and navigate to the project directory

3. Run the app:
   ```
   preswald run
   ```

## How to Deploy

To deploy this app to Structured Cloud:

1. Get an API key from [app.preswald.com](https://app.preswald.com/)
2. Deploy using the following command:
   ```
   preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
   ```

## Live Demo

[Link to the deployed app will be added after deployment]