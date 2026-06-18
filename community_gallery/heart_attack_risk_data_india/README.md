## Overview
This Preswald application loads and analyzes a cardiovascular dataset (heart_attack_prediction_india). It provides:

1. Aggregation of heart attack risk by state
2. A correlation heatmap of selected numeric features
3. Additional visualizations (pie chart, box plot, histogram)
4. An interactive age-based filter plus a configurable bubble chart
The dataset is collected from Kaggle: https://www.kaggle.com/datasets/ankushpanday2/heart-attack-risk-and-prediction-dataset-in-india
The csv file can be found here : https://drive.google.com/file/d/19MYbprJG44NGOfNr0ESZB-R4bwzCwjFk/view?usp=drive_link
This can be placed in data folder

## Prerequisites
1. Python 3.10+
2. Install preswald using pip install preswald
3. A CSV file called heart_attack_prediction_india.csv placed in a data/ folder.

## How to run
1. Firstly, install preswald
2. Confirm whether correct dataset is referred in preswald.toml file
3. Place the CSV file in data folder
4. Run "preswald run" command

## Features

1. Bar Chart: Average heart attack risk by state
2. Correlation Heatmap: Shows correlations among numeric columns
3. Pie Chart: Distribution of heart attack history
4. Box Plot: Systolic blood pressure by gender
5. Histogram: Age distribution
6. Age-based Filter + Bubble Chart: Filter patients by age range and choose any numeric column for the Y-axis; bubble size represents cholesterol level

## Technical details

1. Preswald Connection: The code calls connect() to read preswald.toml and register CSV files
2. Data extraction: get_df("heart_attack_prediction_india") loads the CSV into a pandas DataFrame.
3. SQL Queries: We use query(sql, "heart_attack_prediction_india") to run SQL statements on the dataset for grouping by state and calculating averages and other metrics.
4. Each visualization uses plotly to be plotted on the UI

Production URL : https://heart-attack-risk-data-india-251273-rhum9agv-ndjz2ws6la-ue.a.run.app
