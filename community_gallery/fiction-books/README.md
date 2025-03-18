# Fiction Books Data Analysis

## Overview

This analysis explores a dataset of fiction books, focusing on user ratings and publication years. It provides interactive filters to refine data based on user preferences.

## Key Steps

1. **Data Loading**: Connect to the data source and load the "my_dataset" into a DataFrame.
2. **Genre Filtering**: Filter the dataset to include only fiction books.
3. **Interactive Filters**:
   - **User Rating**: Use a slider to select books based on user ratings.
   - **Publication Year**: Select a year to filter books published after that year.
4. **Data Querying**: Retrieve filtered data using SQL queries.
5. **Visualization**: Generate a scatter plot of user ratings versus reviews, colored by publication year.

## Technologies Used

- **Preswald**: For interactive data analysis and visualization.
- **Plotly Express**: To create interactive plots.

## Expected Outcomes

- **Filtered Data**: View fiction books based on selected ratings and publication years.
- **Interactive Exploration**: Adjust filters dynamically to explore different subsets of data.
- **Visual Insights**: Understand the relationship between user ratings and reviews through interactive plots.

## Dataset Source

[Amazon Top 50 Bestselling Books 2009-2019](https://www.kaggle.com/datasets/sootersaalu/amazon-top-50-bestselling-books-2009-2019)

## Running the App

To run the app, execute the following command:

```
preswarld run
```

## Deploy the App

To deploy this app, create a preswald API key:

1. Go to [preswald.com](https://preswald.com).
2. Create a New Organization (top left corner).
3. Navigate to **Settings > API Keys**.
4. Generate and copy your Preswald API key.

Then, add your GitHub username and Preswald API key in the following command:

```
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```