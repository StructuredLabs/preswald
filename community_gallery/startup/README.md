# Preswald Project

## Setup

1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`

# Startup Growth and Funding Trends Analysis

## Dataset Source

This analysis uses the "Startup Growth and Funding Trends" dataset from Kaggle, available at: [https://www.kaggle.com/datasets/samayashar/startup-growth-and-funding-trends](https://www.kaggle.com/datasets/samayashar/startup-growth-and-funding-trends)

## App Description

This Preswald application provides a visual exploration of startup data, focusing on key metrics such as Funding Amount, Valuation, Revenue, Employees, and Industry. It helps uncover trends and relationships within the startup ecosystem through interactive charts and data visualizations.

The app includes the following visualizations:

- **Funding Amount vs. Valuation:** A scatter plot showing the relationship between funding and valuation.
- **Startup Count by Industry:** A bar chart displaying the distribution of startups across different industries.
- **Revenue vs. Employees:** A scatter plot illustrating the correlation between company size and revenue.
- **Funding Amount Distribution by Region:** A box plot comparing funding across different regions.
- **Distribution of Founding Year:** A histogram showing the historical trends in startup creation.
- **Valuation Distribution by Industry:** A violin plot to visualize the distribution of valuations within industries.
- **Startup Count by Exit Status:** A bar chart showing the outcomes of the startups.
- **Feature Correlation Heatmap:** A heatmap displaying the correlations between numerical features.
- **Valuation vs. Revenue:** a scatter plot showing the relationship between those two columns.
- **Full Dataset Table:** A table displaying the raw data.

## How to Run

1.  Clone the repository.
2.  Ensure you have Preswald installed (`pip install preswald`).
3.  Place the `startup_data.csv` file (downloaded from Kaggle) in the `data/` folder of your project.
4.  Update your `preswald.toml` file to include the data source:

    ```toml
    [datasources]
    startup_data = { path = "data/startup_data.csv" }
    ```

5.  Run the application using the following command:

    ```bash
    preswald run hello.py
    ```

6.  Open the provided URL in your browser to view the app.

## How to Deploy

1.  Obtain your Preswald API key from [app.preswald.com](https://app.preswald.com/).
2.  Deploy the application to Structured Cloud using the following command:

    ```bash
    preswald deploy --target structured --github <your-github-username> --api-key <your-api-key> hello.py
    ```

    Replace `<your-github-username>` and `<your-api-key>` with your GitHub username and Preswald API key, respectively.

3.  Open the provided deployment URL in your browser to view the deployed app.
