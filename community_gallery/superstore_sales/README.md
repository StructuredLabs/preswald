# Superstore Sales Analysis - Preswald Project

This project is a Superstore Sales Analysis application built using Preswald. It enables users to interactively explore sales data, visualize trends, and filter records based on sales thresholds.

## Project Structure
```
community_gallery/superstore_sales_analysis/
├── hello.py
├── data/
│   ├── train.csv
├── README.md
├── preswald.toml
```

## Setup Instructions

Ensure you have Preswald installed. If not, install it using:
```bash
pip install preswald
```

Modify the `preswald.toml` file to match your dataset:
```toml
[project]
title = "Superstore Sales Analysis"
version = "1.1.0"
port = 8501
slug = "superstore-sales-analysis"
entrypoint = "hello.py"

[branding]
name = "Superstore Sales Insights"
primaryColor = "#ff6f61"

[data.superstore_sales]
type = "csv"
path = "data/train.csv"
encoding = "utf-8"

[logging]
level = "INFO"
```

Run the application using:
```bash
preswald run hello.py
```
This will start the application locally on `http://localhost:8501/`

## Features

- Interactive sales data analysis with filtering and threshold adjustments
- Top 5 sales records displayed for quick insights
- Sales breakdown by sub-category in a graphical format
- Search and sorting functionality for efficient data exploration
- Pagination for large datasets to ensure smooth user experience
- Responsive UI with real-time slider updates

## Deployment to Structured Cloud

To deploy the app, first generate an API key from the Preswald dashboard. Navigate to the settings section and create an API key.

Use the following command to deploy the application:
```bash
preswald deploy --target structured --github <your-github-username> --api-key <your-api-key> hello.py
```
Replace `<your-github-username>` and `<your-api-key>` with actual credentials.

After deployment, a live preview link will be provided where the app can be tested.

## Contributing

To contribute to this project, first fork the Preswald repository.

Clone your forked repository:
```bash
git clone https://github.com/your-github-username/preswald.git
cd preswald
```

Create a new folder inside `community_gallery/` and move your files into it:
```bash
cd community_gallery
mkdir superstore_sales_analysis
cd superstore_sales_analysis
mv path/to/hello.py .
mv path/to/data/train.csv data/
```

Commit and push your changes:
```bash
git add .
git commit -m "Added Superstore Sales Analysis example"
git push origin main
```
