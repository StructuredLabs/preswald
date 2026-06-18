# Preswald Project

# Github Issues Explorer

## Dataset Source

The dataset used in this project is derived from **Github Issues data**. \
Link - https://www.kaggle.com/datasets/davidshinn/github-issues/data

The dataset used consists of a CSV file of 50000 rows `github_issues_sample.csv` sampled from a larger dataset from Kaggle, which includes the following columns:

- **Issue URL**: URL of the github issue
- **Issue Title**: Title of the issue
- **Body**: Body of the issue

## App Features

- **Programming Language Frequency**: A interactive pie chart showing number and % of mentions of programming languages in issues.
- **Sentiment Analysis**: A historgam showing the number of issues based on the sentiments from negative to positive.
- **Word Cloud Scatter**: A interactive 3D scatter point cloud showing the commonly used words in github issues.
- **Issues Table**: A table which can be manipulated using 2 sliders - the number of rows and the minimum sentiment which helps the user see issues with more positive sentiments.

## How to Run the App Locally

### Prerequisites

1. **Install Python**: Ensure you have Python 3.11 or higher installed.
2. **Install Required Packages**: The project relies on the following Python libraries:

   - `pandas` for data manipulation
   - `plotly` for visualizations
   - `preswald` for app functionality
   - Other dependencies as required for your environment

   To install the required packages, run the following command in your terminal:

   ```bash
   pip install pandas plotly preswald
   ```

### Running the App

1. **Clone the repository** or download the files.
2. **Prepare the Dataset**: Make sure the csv file is in the correct directory.

3. **Run the App**:
   Once all dependencies are installed and your dataset is in place, you can run the app locally by using the following command in your terminal:

   ```bash
   preswald run
   ```

   This will start the app locally, and you can open it in your web browser at the provided local URL (e.g., `http://127.0.0.1:8000`).

## How to Deploy the App

### 1. **Deploy Locally with Preswald** (for Development)

Once you have the app working locally, you can deploy it using **Preswald**'s deployment tools.

- Make sure you're logged in to Preswald and have the necessary API keys. You can generate an API key by visiting [Preswald's API Keys page](https://app.preswald.com/settings/api-keys).

- Run the following command to deploy the app to **Preswald**:
  ```bash
  preswald deploy --target structured --github --api-key YOUR_API_KEY
  ```

Replace `YOUR_API_KEY` with your actual Preswald API key.

### 2. **Deployment Steps**:

- **Create a New Organization**: Go to [Preswald's website](https://app.preswald.com/) and create a new organization.
- **Generate an API Key**: Navigate to **Settings > API Keys** to generate a new API key.
- **Deploy**: Use the `preswald deploy` command to deploy your app.

After deployment, a live preview link will be generated. You can share the link or use it to access the app from any device.

Enjoy exploring github issues through this interactive dashboard!
