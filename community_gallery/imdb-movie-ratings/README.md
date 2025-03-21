# Movie Explorer: Ratings, Trends & Fun Facts

## Overview
Movie Explorer is an interactive application built using **Preswald** providing insights into IMDb movie ratings, trends, and fun facts. This app allows users to explore movie ratings based on different filters, visualize trends, and uncover interesting statistics from the IMDb dataset.

## Dataset
The dataset used in this project is the **IMDb Movies Dataset**, stored as a CSV file (`movies_csv`). The dataset contains the following columns:


- `name`: Movie title
- `genres`: Genres associated with the movie (separated by `;`)
- `year`: Release year of the movie
- `rating`: Average IMDb rating (out of 10)
- `num_raters`: Number of users who rated the movie
- `num_reviews`: Number of reviews for the movie
- `run_length`: Runtime of the movie in minutes

This dataset can be used for:
- Analyzing movie trends over the years.
- Finding highly rated or poorly rated movies.
- Understanding the correlation between runtime and ratings.
- Exploring the popularity of genres.

You can access the dataset from this link: https://www.kaggle.com/datasets/krishnanshverma/imdb-movies-dataset

## Features
The app provides the following functionalities:

1. **Filtering Movies:**
   - Users can filter movies by **genre** or **starting letter of the movie name**.
   - They can also filter by **maximum rating** and **maximum release year**.

2. **Displaying Filtered Results:**
   - A table shows the filtered list of movies along with key details (name, genres, year, rating, number of raters, number of reviews, runtime).

3. **Visualizations:**
   - **Number of Movies Released Per Year** - Line chart showing the count of movies released each year.
   - **Average Movie Rating Per Year** - Line chart displaying how movie ratings have changed over time.
   - **Duration vs Average Rating** - Scatter plot showing the relationship between runtime and average rating.

4. **Fun Movie Facts:**
   - Users can select a fun fact category to discover insights such as:
     - Highest and lowest-rated movies
     - Longest and shortest movies
     - Most and least-rated movies
     - Earliest and latest released movies

## How to Run the Application

### Prerequisites
Ensure that you have Python installed and the required dependencies installed. You will also need **Preswald** for running the interactive application.

### Installation Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd imdb-movie-ratings
   ```

2. Install dependencies:
   ```bash
   pip install pandas plotly preswald
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
[IMDb Movie Explorer](https://imdb-movie-ratings-137736-yqzjdbfn-ndjz2ws6la-ue.a.run.app/)

## Conclusion
Movie Explorer is a fun and insightful tool for movie enthusiasts who want to explore IMDb data. With interactive filtering, data visualization, and fun movie facts, it makes discovering and analyzing movies easy and enjoyable!