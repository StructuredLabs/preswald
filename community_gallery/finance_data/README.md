# Adult Income Analysis

## Dataset Source

This project uses the [Adult Income dataset](https://www.kaggle.com/datasets/wenruliu/adult-income-dataset/data) sourced from Kaggle. The dataset contains demographic information of adults and their income level, which is used to predict whether an individual earns more than $50K/year based on features such as age, education, occupation, and hours worked per week.

### Dataset Columns:

- `age`: Age of the individual.
- `workclass`: Type of employment (e.g., Private, Self-emp, Government).
- `fnlwgt`: Final weight used for the dataset's statistical analysis.
- `education`: Highest level of education.
- `educational-num`: Number of years of education.
- `marital-status`: Marital status (e.g., Married, Single).
- `occupation`: Occupation of the individual.
- `relationship`: Relationship status (e.g., Husband, Wife).
- `race`: Race of the individual.
- `gender`: Gender of the individual.
- `capital-gain`: Capital gain income.
- `capital-loss`: Capital loss income.
- `hours-per-week`: Number of hours worked per week.
- `native-country`: Country of origin.
- `income`: Income level (>=50K, <50K).

## What App Does

This application provides an analysis of the Adult Income dataset with the following features:

- **Age Threshold Filter**: Users can filter data based on a minimum age threshold to analyze income levels across different age groups.
- **Data Visualizations**: The app provides interactive charts to explore various relationships in the dataset, such as:
  - **Scatter Plot**: Displays the relationship between education level and hours worked per week.
  - **Histogram**: Shows the age distribution of individuals by income level.
  - **Box Plot**: Compares work hours per week across different income levels.
  - **Bar Chart**: Shows the count of individuals in different occupations by income level.
  - **Pie Chart**: Displays the proportion of individuals earning above and below $50K.
  - **Heatmap**: Visualizes the correlation matrix of numerical features in the dataset.

## How to Run and Deploy

To Run App: preswald run
To Deploy: preswald deploy --target structured

### Requirements

1. Python 3.x
2. Install the required libraries:
   ```bash
   pip install preswald plotly
   ```
