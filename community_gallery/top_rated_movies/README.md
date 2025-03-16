# 🎬 Top Rated Movies Dashboard

A Preswald-powered interactive dashboard that allows users to explore and visualize data about top-rated movies.

## 📊 About the Dataset

The dashboard uses the "top_rated_movies.csv" dataset which contains information about popular and highly-rated movies, including:

- Movie ID
- Original titles
- Overview descriptions
- Release dates
- Popularity scores
- Vote averages
- Vote counts

## 🚀 Features

This dashboard application provides:

- Interactive data preview with filtering capabilities
- Dynamic popularity threshold filtering using sliders
- SQL query functionality to manipulate and edit movie data
- Visualization of movie popularity using interactive Plotly charts

## 🔧 How to Run Locally

1. Make sure you have Python installed on your system.

2. Install the required dependencies:
   ```bash
   pip install preswald
   ```

3. Run the application:
   ```bash
   preswald run hello.py
   ```

4. Open your browser and navigate to the URL displayed in the terminal (typically http://localhost:8501).

## 📦 Deployment

To deploy this application:

1. Configure your deployment settings in the preswald.toml file.

2. Use the Preswald deployment command:
   ```bash
   preswald deploy
   ```

3. Your application will be available at the deployed URL.