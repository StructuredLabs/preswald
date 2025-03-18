## AI Companies Dashboard

An interactive Preswald application that provides analytical insights into top AI companies, including revenue, employee satisfaction, industry classification, and geographical distribution.

Link to my Deployed app : Link[https://new-coding-assessment-279836-ssvcjex7.preswald.app/](https://new-coding-assessment-279836-ssvcjex7.preswald.app/)

## Folder Structure

```
community_gallery/Top_Ai_Companies/
├── hello.py
├── data/
    ├── Ai_Companies.csv
├── README.md

```

## Dataset Source

Dataset Source
The dataset is sourced from Kaggle - AI Companies Dataset and includes key details about leading AI firms worldwide.
The dataset is sourced from **[Kaggle - AI Companies Dataset](https://www.kaggle.com/datasets/raniritu/ai-companies)**.

Dataset Details
The dataset contains information about AI companies, including:
Company Name: The official name of the AI company.
Description: A brief summary of what the company specializes in.
Headquarters: The city and country where the company is based.
Founded Year: The year the company was established.
Annual Revenue: The estimated yearly revenue of the company.
Glassdoor Score: Employee satisfaction ratings collected from Glassdoor.
This dataset helps in understanding the landscape of AI companies, their financial performance, and their work environment.

## Data Cleaning & Processing

Before generating visualizations, the data is:
Converted to numerical format for revenue values (million and billion are transformed).
Checked for missing values in the Revenue and Glassdoor Score columns.
Extracted country names from the Headquarters column for geographical insights.
Standardized Glassdoor Score: Ratings of 5.0 were adjusted to 4.5 to align with scoring conventions.
Added a Category Feature: Extracted industry classification (e.g., Cybersecurity, Robotics, Healthcare).

## App Features

1. Top AI Companies by Revenue (Bar Chart)
   Highlights the top 5 AI companies based on revenue.

2. Growth of AI Companies Over Time (Line Chart)
   Displays the number of AI companies founded per year to track industry expansion.

3. Geographical Distribution of AI Companies (Choropleth Map)
   Shows the global distribution of AI companies by country.

4. Distribution of Company Revenues (Histogram)
   Analyzes revenue distribution across AI companies.

5. Correlation Heatmap
   Displays relationships between founding year, revenue, and employee ratings.

6. Glassdoor Score vs. Revenue (Scatter Plot)
   Examines whether employee satisfaction is correlated with company revenue.

7. Industry-Based Revenue & Glassdoor Score (Bubble Chart)
   Groups companies by industry classification (e.g., Cybersecurity, Robotics, Healthcare) and visualizes revenue trends.

## How to Run Locally

Install Preswald:
pip install preswald

Clone this repository and navigate to the project directory.

Run the app:
preswald run

Open localhost:8501 in a web browser.

## How to Deploy

To deploy this app on Preswald:

Obtain an API key from [app.preswald.com](https://app.preswald.com)

Deploy using the following command:
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
