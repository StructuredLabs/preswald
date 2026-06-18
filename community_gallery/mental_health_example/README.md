# Preswald Project

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`

# 📊 Mental Health Care Trends App

## 📌 Overview
This **Preswald app** provides insights into **mental health care trends in the U.S.** using **data visualization and interactive filtering**.

## 📈 Features
- **Dataset Preview:** View the first 20 rows of the dataset.
- **Interactive Filtering:** Adjust the threshold for the **percentage of people receiving care** using a slider.
- **State-Level Trends:** A **bar chart** visualizes mental health care data for the **top 15 states**, sorted by percentage.

## 🗂 Dataset Source
- **Name:** Mental Health Care in the Last 4 Weeks
 - Mental Health Data
- **Provider:** [U.S. Department of Health & Human Services](https://catalog.data.gov/dataset/mental-health-care-in-the-last-4-weeks)
- **Description:** "The U.S. Census Bureau, in collaboration with five federal agencies, launched the Household Pulse Survey to produce data on the social and economic impacts of Covid-19 on American households. The Household Pulse Survey was designed to gauge the impact of the pandemic on employment status, consumer spending, food security, housing, education disruptions, and dimensions of physical and mental wellness."

## 🚀 How to Run Locally
1. **Install Preswald**:
   pip install preswald
2. **Run the app**:
    preswald run
3. **Deploy to Preswald Cloud**:
    preswald deploy --target structured --github <your-github-username> --api-key <your-api-key>

##Check out the live app here: https://my-example-project-161201-epowkgea.preswald.app

