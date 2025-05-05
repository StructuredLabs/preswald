# Preswald Project

## The dataset source:
Dataset Source

The dataset used in this project is the Iris dataset, which is a well-known dataset in the field of machine learning and statistics. It consists of 150 samples of iris flowers categorized into three species: Setosa, Versicolor, and Virginica. Each sample includes measurements of:

Sepal Length (cm)

Sepal Width (cm)

Petal Length (cm)

Petal Width (cm)

Species (the flower category)

The dataset is publicly available from multiple sources, including Kaggle and the UCI Machine Learning Repository.
https://www.kaggle.com/datasets/himanshunakrani/iris-dataset



## Application Overview:

This Preswald app provides an interactive visualization of the Iris dataset. The key features include:

Dynamic Filtering: Users can adjust the Petal Length Threshold using a slider to filter the dataset dynamically.

Tabular View: Displays the filtered dataset in a table.

Scatter Plot Visualization: Plots the Sepal Length vs. Sepal Width for different species using distinct colors.

Interactive UI: Users can explore how different threshold values affect the dataset visualization.

How to run and deploy it.

Prerequisites

Ensure you have Python installed along with preswald. If you haven’t installed it yet, run:

You can activate python virtual environment using:

conda create --name preswald-env python=3.10
conda activate preswald-env

pip install preswald

Steps to Run Locally

Fork  the Repository:
open the repository 
cd <your-repo-folder>

Initialize the Preswald Project:

preswald init my_iris_example
cd my_iris_example

Place the Iris Dataset:

Ensure Iris.csv is located in the data/ folder of your project.

Update the data source in preswald.toml

Run the Application:

preswald run 

Open the provided local URL in your browser to view the app.

How to Deploy the App

Step 1: Get an API Key

Go to app.preswald.com

Create an organization (if not already created)

Navigate to Settings > API Keys

Generate and copy your Preswald API key

Step 2: Deploy the App

Run the following command, replacing <your-github-username> and <structured-api-key> with your credentials:

preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py

Step 3: Verify Deployment

Once deployment is complete, a live preview link will be provided. Open the link in your browser to verify that your app is running successfully.

## Running App Link: https://preswald-my-iris-example-571176-lqvvrxsy-ndjz2ws6la-ue.a.run.app/

