# Child BMI Data Visualization

This pull request adds an interactive application that visualizes child BMI data extracted from a CSV file. The data includes school year, hospital details, sex, and four key BMI indicators: Underweight, Healthy Weight, Overweight, and Obese.

## Key Features

- **Data Transformation:**  
  Converts the raw, wide-format BMI data into a long format, making it easier to compare different BMI categories side by side.

- **Data Aggregation:**  
  Aggregates BMI percentages by school year and BMI category (using averages) to provide a clear, comparative overview.

- **Grouped Bar Chart:**  
  Displays an interactive grouped bar chart that shows the average BMI distribution across all school years. Each BMI category is color-coded for quick visual differentiation.

- **Trend Line Chart:**  
  Features a line chart with markers that connects average BMI values over time. This visualization highlights trends and shifts in BMI categories across the years.

- **Dynamic Year Filtering:**  
  Implements a slider that allows users to select a specific school year. When a year is chosen, a detailed bar chart updates dynamically to display the BMI distribution for that year.

- **Comprehensive Data Tables:**  
  Presents both the raw and aggregated data in table format for users who wish to inspect the underlying numbers in detail.

## Overview

This application delivers a comprehensive and interactive view of child BMI trends, enabling users to:

- Quickly compare BMI category distributions across different school years.
- Observe long-term trends with smooth, connected line charts.
- Drill down into specific school years using dynamic filtering.

The visualization tools provided here enhance data interpretability, making it easier to draw insights from the BMI dataset.
