# Sleep Health and Lifestyle Analysis

## Dataset Source
This project uses the Sleep Health and Lifestyle Dataset from Kaggle, which contains information about sleep patterns, BMI categories, and sleep disorders across different categories.
Reference Link: https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset/data

## What This App Does
This application provides:
- An overview of sleep health metrics across the dataset
- Interactive filtering by sleep duration using a slider
- Visualizations showing the relationship between gender, BMI category, and sleep disorders
- A data table displaying the filtered dataset records

## How to Run and Deploy

1: Install preswald. You can create a new virtual environment or install other requirements as needed.
- pip install preswald
2: Download the dataset from the provided source. (https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset/data)
3: You can execute the hello.py file using: preswald run to initialize and run the application locally.
4: To deploy the application, execute the following code in your terminal:
    preswald deploy --target structured --github YOUR_GITHUB_USERNAME --api-key YOUR_API_KEY
Note: You need to replace "YOUR_GITHUB_USERNAME" with your Github Profile username (all lowercase) and "YOUR_API_KEY" with the API key generated from "app.preswald.com"


## Live Demo
[Sleep Health Dashboard](https://coding-assessment-466795-3ewu6miz-ndjz2ws6la-ue.a.run.app)

Note: This app is developed taking the 30-minute time limitation into account. The visual dashboard and the storyline can further be improved further with more time.