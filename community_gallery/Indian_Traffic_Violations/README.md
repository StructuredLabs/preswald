# Indian Traffic Violations Analysis Dashboard

## Overview

This project provides an interactive dashboard to analyze Indian traffic violations data using Preswald's UI components. The dashboard enables users to explore the dataset from multiple perspectives, including violation type analysis, temporal trends, and vehicle type distribution.

## Data Description

The dataset (`Indian_Traffic_Violations.csv`) contains records of traffic violations in India, with key columns such as:

- **Violation:** The type or category of traffic violation.
- **Date:** The date when the violation occurred.
- **State:** The state in India where the violation took place.
- **Vehicle_Type:** The type of vehicle involved in the violation.

## App Features

- **Violation Type Analysis:** Displays a bar chart and table summarizing the frequency of different violation types.
- **Temporal Trends:** Aggregates the data by month (limited to the last 50 months) and visualizes trends over time using a line chart and table.
- **Vehicle Type Analysis:** Illustrates the distribution of vehicle types involved in violations with a pie chart and table.
- **Filtering:** Provides options to filter the dataset by state (if available), allowing users to focus on specific regions.

## How to Run

1. **Set Up Your Environment**

   ```bash
   # Install Preswald and other libraries
   pip install preswald pandas numpy matplotlib plotly scikit-learn

   # Create a new project directory
   preswald init my_dashboard
   cd my_dashboard
   ```

2. **Configure Data Source**
   Create a `preswald.toml` file in your project directory with the following content:

   ```toml
   [data.Indian_Traffic_Violations]
   path = "./data/Indian_Traffic_Violations.csv"
   ```

3. **Download the Dataset**
   Download the Indian_Traffic_Violations dataset and save it as `Indian_Traffic_Violations.csv` in a `data` folder in your project directory.

4. **Run the App Locally**
   ```bash
   preswald run hello.py
   ```
   This will start a local development server, and you can access the dashboard at the URL shown in the terminal.

## Deployment

Deploy to Structured Cloud:

```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```

Replace `<your-github-username>` and `<structured-api-key>` with your credentials.
