# Walmart Customer Purchases Analysis

## Overview

This interactive dashboard analyzes customer purchase behavior using the Walmart Customer Purchase dataset. The application offers insights into various customer demographics and purchasing patterns. It allows for interactive exploration of the data with visualizations like histograms, bar charts, box plots, and clustering results.

## Dataset Source

The dataset used in this analysis is the **Walmart Customer Purchase Behavior Dataset**, which is available on Kaggle. You can access the dataset [here](https://www.kaggle.com/datasets/logiccraftbyhimanshi/walmart-customer-purchase-behavior-dataset).

The dataset contains various customer features including:
- **Age**: The age of the customer.
- **Gender**: The gender of the customer.
- **Category**: The category of the products purchased.
- **Purchase Amount**: The total purchase amount for the transaction.
- **Rating**: The rating the customer gave for the product.
- **Payment Method**: The payment method used by the customer.
- **Repeat Customer**: Whether the customer is a repeat customer (Yes/No).
- **Discount Applied**: Whether a discount was applied to the purchase (Yes/No).

## Features and Visualizations

The application performs the following analyses:
1. **Data Overview**: Provides an initial look at the dataset, including the number of rows and columns.
2. **Missing Values Check**: Identifies and handles any missing values in the dataset.
3. **Histograms**: Plots the distribution of **Age** and **Purchase Amount**.
4. **Bar Plots**: Displays the count of different **Gender** and **Payment Methods**.
5. **Box Plot**: Shows the distribution of **Purchase Amount** by **Category**.
6. **Violin Plot**: Displays the distribution of **Ratings** by **Gender**.
7. **Clustering with K-Means**: Applies K-Means clustering to segment customers into different groups.
   - **Clusters** are visualized using PCA (Principal Component Analysis) to reduce the dimensionality and display it in 2D.

The clusters identified are:
- **Cluster 0**: High-Spending Repeat Customers
- **Cluster 1**: Discount-Sensitive Shoppers
- **Cluster 2**: Budget-Conscious Shoppers
- **Cluster 3**: Occasional High-Spenders

## How It Works

1. **Data Preprocessing**:
   - Missing values are handled by replacing them with the median for numeric columns.
   - Categorical features like `Repeat_Customer` and `Discount_Applied` are mapped to numeric values (Yes=1, No=0).
   - One-hot encoding is applied to the `Category` and `Payment_Method` columns to convert them into numerical features.

2. **Scaling**:
   - Numerical features are scaled using **StandardScaler** to standardize the data before applying the clustering algorithm.

3. **Clustering**:
   - The optimal number of clusters (`k=4`) is determined using the **Elbow Method**.
   - **K-Means Clustering** is applied to the scaled dataset, and customers are grouped into different segments.

4. **Visualization**:
   - **PCA** is used for dimensionality reduction to visualize the customer segments in 2D.

## How to Run and Deploy

### Prerequisites

- Python 3.x
- Install required packages using:
  ```bash
  pip install pandas plotly scikit-learn preswald