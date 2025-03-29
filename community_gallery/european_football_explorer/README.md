# European Football League Explorer - Preswald App

## Overview

This Preswald app allows users to explore and analyze statistics from the top European football leagues.  It provides interactive filters to view team performance based on different criteria, along with visualizations to highlight key trends and insights.

## Dataset Source

The data is sourced from [Kaggle](https://www.kaggle.com/datasets/jehanbhathena/big-5-european-football-leagues-stats): "Top 5 European Football Leagues Stats" dataset.  It includes team statistics from the Premier League, La Liga, Serie A, Bundesliga, and Ligue 1 for seasons from 2010/11 to 2020/21.

## Functionality

The app allows users to:

*   **Filter by Season:**  Select a starting year to analyze data from that season onwards.
*   **Filter by Performance:**  Adjust sliders to set minimum thresholds for points and goals scored.
*   **Visualize Team Performance:**  Explore data through interactive scatter plots and bar charts.
*   **View Top Performers:**  See a table of teams meeting the specified criteria, along with their key statistics.

## How to Run and Deploy

1.  **Clone the Preswald repository:**

    ```
    git clone https://github.com/<your-github-username>/Preswald.git
    cd Preswald
    ```

    Replace `<your-github-username>` with your GitHub username.
2.  **Navigate to the project directory:**

    ```
    cd community_gallery/european_football_stats/
    ```
3.  **Install Preswald:**

    ```
    pip install preswald
    ```
    (It's recommended to use a virtual environment)
4.  **Run the app:**

    ```
    preswald run hello.py
    ```
5.  **Deploy to Structured Cloud:**

    *   Get an API key from [app.preswald.com](http://app.preswald.com/).
    *   Deploy using the following command:

        ```
        preswald deploy --target structured --github <your-github-username> --api-key <your-api-key> hello.py
        ```

        Replace `<your-github-username>` and `<your-api-key>` with your credentials.
6. **Open the live preview link** provided after deployment to view your app.

## Key Libraries

*   Preswald
*   Pandas
*   Plotly

## Potential Enhancements

*   Add more granular filtering options (e.g., specific leagues, team names).
*   Implement more advanced visualizations (e.g., heatmaps, time series charts).
*   Incorporate machine learning models to predict match outcomes.

## Author

[Amudhan Muthaiah]
