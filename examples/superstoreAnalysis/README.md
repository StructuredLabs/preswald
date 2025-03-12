
# Superstore Analytics App

## Overview

This project leverages data from a **Superstore dataset** to provide visual insights into sales and profit analysis, quantity vs. discount relationships, and the impact of shipping costs. The app allows users to interactively filter data and view various visualizations to gain insights into sales, profit, and customer segments.

## Dataset

The dataset used in this project is a sample of **Superstore data**, which includes records of orders, sales, and other related fields. It is available on Kaggle.

- **Source**: [Superstore Dataset on Kaggle](https://www.kaggle.com/datasets/apoorvaappz/global-super-store-dataset?resource=download)
- **File**: The data is stored in `data/Global_Superstore2.csv`. If you don’t have the dataset, you can download it from the link above and place it in the `data/` directory.

## Features

- **Sales vs. Profit Analysis**: Displays the relationship between sales and profit, categorized by product category.
- **Quantity vs. Discount**: Shows how different quantities correlate with discount levels, categorized by customer segment.
- **Shipping Cost Slider**: A dynamic slider that allows users to filter data based on shipping cost, helping users to explore how shipping impacts sales data.

## Requirements

1. Python 3.x
2. Required libraries:
    - `preswald`
    - `plotly`
    - `pandas`
