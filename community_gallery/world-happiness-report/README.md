# World Happiness Explorer: Insights, Trends & Fun Facts

## Overview
World Happiness Explorer is an interactive application built using **Preswald** providing insights into the World Happiness Report

## Dataset
The dataset used in this project is the **World Happiness Report Dataset**, stored as a CSV file (`data/hcw.csv`). The dataset contains the following columns:

- `country`: Country name
- `happiness_ranking`: Ranking
- `happiness_score`: Happiness score (out of 10)

You can access the dataset from this link: https://www.kaggle.com/datasets/nafayunnoor/happiest-countries-in-the-world-2024

## How to Run the Application

### Prerequisites
Ensure that you have Python installed and the required dependencies installed. You will also need **Preswald** for running the interactive application.

### Installation Steps
1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd world-happiness-report
    ```

2. Install dependencies:
    ```bash
    pip install preswald
    ```

3. Run the application:
    ```bash
    preswald run
    ```

### Deploying the App in Preswald
The app can be deployed in **Preswald Structured Cloud** using the following steps:

1. **Get an API Key**
    - Go to [app.preswald.com](https://app.preswald.com)
    - Create a **New Organization** (top left corner)
    - Navigate to **Settings > API Keys**
    - Generate and copy your **Preswald API Key**

2. **Deploy Your App**
    Run the following command in your terminal, replacing `<your-github-username>` and `<structured-api-key>` with your actual credentials:
    ```bash
    preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
    ```

3. **Verify the Deployment**
    - Once deployment is complete, a **live preview link** will be provided.
    - Open the link in your browser and verify that your app is running.

### Live Demo
You can access the deployed application here:
[World Happiness Explorer](https://hello-928078-9f41lunv-ndjz2ws6la-ue.a.run.app/)

## Conclusion
World Happiness Explorer is a fun and insightful tool for those interested in global happiness trends. With interactive filtering, data visualization, and fun happiness facts, it makes discovering and analyzing happiness data easy and enjoyable!