# 📊 Sales Data Analysis App

This is an interactive data analysis app. It provides visualizations and controls for exploring sales performance data, including quantities sold, sales amounts, product categories, and more.

## 🔧 Features

- **Dynamic Table Viewer**: Use a slider to control how many rows of the dataset to preview.
- **Interactive Histogram**: Select between `Quantity_Sold` or `Sales_Amount` to visualize their distributions.
- **Sales Filtering**: Toggle a checkbox to view only high-performing sales (Sales Amount > 5000).
- **Scatter Plot Visualization**: Explore the relationship between `Quantity_Sold` and `Sales_Amount`, colored by product category.
- **Error Handling**: Gracefully handles missing or misconfigured datasets with alerts.

## 📁 Dataset Requirements


| Column              | Description                         |
|---------------------|-------------------------------------|
| `Product_ID`        | Product identifier                  |
| `Sale_Date`         | Date of the sale                    |
| `Sales_Rep`         | Sales representative name           |
| `Region`            | Sales region                        |
| `Sales_Amount`      | Total revenue from the sale         |
| `Quantity_Sold`     | Units sold                          |
| `Product_Category`  | Category (e.g., Furniture, Food)     |
| `Unit_Cost`         | Cost per unit                       |
| `Unit_Price`        | Selling price per unit              |
| `Customer_Type`     | Customer status (New or Returning)  |
| `Discount`          | Discount applied (e.g., 0.08 = 8%)  |
| `Payment_Method`    | Cash, Credit Card, Bank Transfer... |
| `Sales_Channel`     | Online or Retail                    |
| `Region_and_Sales_Rep` | Combined label for visualizations |


