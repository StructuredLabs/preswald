<h1 align="center">🚗🚢 &nbsp;&nbsp; Automobile Sales Viz App&nbsp;&nbsp; ✈🚅</h1>
<p align="center">
    <image src="./images/logo.png" height="200" width="200" />
</p>


## Dataset Source
Link: https://www.kaggle.com/datasets/ddosad/auto-sales-data/data

## Application Overview

This app provides a comprehensive analysis of automobile sales data, offering insights through various statistical summaries and visualizations. 

Key features include:

- Descriptive Summaries: Detailed statistics for both numerical and categorical features.
- Univariate Analysis: Distribution analysis of individual variables using **histograms**, **box plots**, and **bar charts**.
    - *User Input*: Select the type of chart to display using a `dropdown/selectbox`.
- Bivariate Analysis: **Scatter plots** and **correlation heatmaps** to explore relationships between variables.
    - *User Input*: Use `sliders` to adjust the number of bins
- Multivariate Analysis: Advanced visualizations like sales *trends* over time and *comparisons* across product lines and deal sizes.
    - *User Input*: Enable/diable `checkbox` mor markers for line plot.

## Setup (Bash)
1. Clone the app repository
```sh
$ git clone https://github.com/r3yc0n1c/preswald.git
$ cd preswald/community_gallery/automobile_sales/
```
2. Create and activate a python3 virtualenv
```sh
$ python3 -m venv env
$ source ./env/bin/activate
```
3. Install dependencies
```sh
$ pip install -r requirements.txt
```
4. Download and put the csv data file in `community_gallery/automobile_sales/data/` and call it `auto_sales_data.csv`
5. (Optional) Configure your data connections in `preswald.toml`
6. Run your app
```sh
$ preswald run
Running 'hello.py' on http://localhost:8501 with log level INFO  🎉!
```
7. Open http://localhost:8501 in your browser
8. Make changes in [hello.py](hello.py) to tweak the app.
9. Format the code
```sh
$ ruff --version
$ ruff format
```
10. Deploy Your App to the Cloud

Add sensitive information (passwords, API keys) to `secrets.toml`
```sh
$ preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```
Replace `<your-github-username>` and `<structured-api-key>` with your credentials.


After deployment, use the live preview link from Preswald to view your app.
