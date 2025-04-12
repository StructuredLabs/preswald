# StockFlow

## Dataset Source
- **Dataset Name:** Stock Market Dataset
- **Source:** https://www.kaggle.com/datasets/jacksoncrow/stock-market-dataset?resource=download

## About the App
This app showcases an example of working with the Stock Market Dataset using the Preswald framework. The app demonstrates how to interactively explore and visualize the stock data, and it allows users to understand key trends and patterns.

### What the App Does:
- Loads the Stock Market Dataset.
- Preprocesses and visualizes the data.
- Takes user input to implement basic analysis and generates insights.

## How to Run the App
- Clone the repository to your local machine:

```
  git clone https://github.com/anajag99/preswald.git
  cd preswald/community_gallery/StockFlow_Assessment
```

Install Preswald and other required dependencies:
```
  pip install preswald
```
Run the app locally using the Preswald CLI:

```
  preswald run
```

This will start the app in your local environment.

## How to Deploy the App:
- Make sure you have set up your Preswald account and have an API key from Preswald's platform.
- Deploy the app using the Preswald CLI with the following command:

  ```
  preswald deploy --target structured --github GITHUB_USERNAME --api-key YOUR_API_KEY hello.py
  ```

Replace GITHUB_USERNAME and YOUR_API_KEY with your actual username and API key.

- You should be able to see the deployment status and interact with the deployed app.
  
