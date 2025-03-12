# Startup Data Analysis Dashboard

## Dataset

This project uses the [Startup Growth and Funding Trends](https://www.kaggle.com/datasets/samayashar/startup-growth-and-funding-trends) dataset from Kaggle. The dataset contains information about various startups including:

- Funding information (rounds, amounts, valuation)
- Industry classification
- Revenue and profitability metrics
- Employee count
- Market share percentage
- Year founded
- Geographical region
- Exit status

This rich dataset allows for comprehensive analysis of startup trends across different industries, regions, and time periods.

## Overview

This is an interactive dashboard built with Preswald that allows users to:

- View summary statistics of the startup ecosystem
- Filter startups based on various criteria
- Compare profitable vs non-profitable startups
- Visualize funding trends, industry distribution, and regional comparisons
- Analyze relationships between funding, valuation, and other metrics

## Project Structure

```
startup-trends/
├── data/                 # Dataset directory
│   └── startup_data.csv  # The Kaggle dataset
├── images/               # Image assets
├── index.py              # Main application code
├── preswald.toml         # Configuration file
└── README.md             # This documentation
```

## Getting Started

### Prerequisites

- Python 3.7+
- Git

### Setup Instructions

1. Install Preswald (if not already installed):
   ```
   pip install preswald
   ```

2. Clone the repository:
   ```
   git clone https://github.com/StructuredLabs/preswald.git
   ```

3. Navigate to the example directory:
   ```
   cd preswald/examples/startup-trends/
   ```

4. Run the application:
   ```
   preswald run
   ```

5. Open your browser and navigate to the local URL displayed in your terminal (typically http://localhost:8501)

## Features

- **Interactive Filtering**: Use sliders to dynamically filter data based on funding, valuation, and market share
- **Data Visualization**: Multiple chart types (scatter plots, bar charts, pie charts) for better insight
- **Profitability Analysis**: Compare profitable vs non-profitable startups
- **Industry Comparison**: Visualize distribution across different industries
- **Regional Analysis**: Examine funding patterns across regions

## Deploy

### Deploy Your App to Structured Cloud

Once your app is running locally, you can deploy it to make it accessible online.

#### Get an API key

1. Go to [app.preswald.com](https://app.preswald.com)
2. Create a New Organization (top left corner)
3. Navigate to Settings > API Keys
4. Generate and copy your Preswald API key

#### Deploy your app

Deploy your app using the following command:

```
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> index.py
```

Replace `<your-github-username>` and `<structured-api-key>` with your credentials.

### Issue you might encounter while deploying

If you encounter the following error:
```❌ Deployment failed: 400 Client Error: BAD REQUEST for url: https://deployer.preswald.com/deploy
Deployment failed: Production deployment failed: 400 Client Error: BAD REQUEST for url: https://deployer.preswald.com/deploy ❌
```

One of the reasons for this could be that your GitHub username contains uppercase letters.
Make sure your pass your GitHub username in lowercase.

#### Verify the deployment

Once deployment is complete, a live preview link will be provided. Open the link in your browser and verify that your app is running.

