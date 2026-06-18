# Grocery Data Analysis App

## Dataset Source
The dataset used in this app is grocery inventory data in a CSV file, sourced from https://www.kaggle.com/datasets/willianoliveiragibin/grocery-inventory. It contains information on various grocery items with features including unit price, inventory turnover rate, order dates, etc.

## What the App Does
The app filters and visualizes the grocery data, specifically focusing on inventory turnover rates of different categories of groceries and the relation between turnover rates and unit prices of items. It also offers dynamic filtering of the data based on a user inputted threshold for inventory turnover rate.

## How to Run and Deploy It
1. Clone the repository:
`git clone https://github.com/antoinedang/preswald-fork`
2. Enter the app's directory:
`cd community_gallery/grocery-inventory`
2. Install dependencies:
`pip install preswald`
3. Run the app locally:
`python hello.py`
4. Deploy the app:
`preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py`
Once deployed, access the live preview link provided in the command output.
