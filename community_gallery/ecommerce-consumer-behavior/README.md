# E-commerce Consumer Behavior Analysis App

This example contains an interactive Preswald app that analyzes customer behavior data from an e-commerce dataset. The app provides rich visualizations, filtering options, and fun facts to help you understand key factors driving customer satisfaction.

Check out the deployed application [here](https://ecommerce-example-485877-xosnolut-ndjz2ws6la-ue.a.run.app/)!

## Dataset Source

[Kaggle link](https://www.kaggle.com/datasets/salahuddinahmedshuvo/ecommerce-consumer-behavior-analysis-data?resource=download)

## What the App Does

The E-commerce Consumer Behavior Analysis App provides an interactive dashboard that:

- Filters Customer Data:
  Users can filter customers by purchase category, channel, and maximum purchase amount.

- Displays Customer Data:
  The app shows a table of the filtered data. Additionally, users can choose which columns to display using checkboxes.

### Visualizations:

- Scatter Plot: Displays the relationship between Age and Purchase Amount, colored by purchase channel.
- Bar Chart: Shows the average purchase amount per category.
- Pie Chart: Illustrates the distribution of payment methods.
- Box Plot: Visualizes purchase amount distributions across different income levels.
- Correlation Heatmap: Displays correlations between key numerical variables related to customer satisfaction.

### Factors affecting customer satisfaction

The final part of the example explores the corrolation betweeen different key factors in the dataset and customer satisfaction.

### Fun Facts Section:

An interactive section that reveals interesting insights (e.g., highest purchase amount, fastest decision time, etc.) from the dataset.

## Setup

1. Configure your data connections in `preswald.toml`, or download the dataset from the above link and place it in the `data/` folder and verify the path in `preswald.toml`:

```
[data.ecommerce_consumer_behavior_csv]
type = "csv"
path = "data/Ecommerce_Consumer_Behavior_Analysis_Data.csv"
```

2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run the app locally with `preswald run`
