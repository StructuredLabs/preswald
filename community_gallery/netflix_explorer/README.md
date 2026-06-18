# Preswald Project

# Netflix Content Explorer

## Dataset Source

- **Source**: [Netflix Movies and TV Shows on Kaggle](https://www.kaggle.com/datasets/shivamb/netflix-shows)
- **File**: `netflix_titles.csv`
- **Note**: This example uses a trimmed version of the original `netflix_titles.csv` (500 rows, ~200-300 KB) to fit within Preswald’s deployment size limits. The full dataset (~3.5 MB) caused a `413 Request Entity Too Large` error during deployment.

### How to Generate the Trimmed Dataset

To replicate the trimmed dataset:

1. Download `netflix_titles.csv` from Kaggle.
2. Run the following Python script in your project directory:
   ```python
   import pandas as pd
   df = pd.read_csv("data/netflix_titles.csv")
   trimmed_df = df.sample(n=500, random_state=42)
   trimmed_df.to_csv("data/netflix_titles_trimmed.csv", index=False)
   ```
3. Delete `netflix_titles.csv` and rename `netflix_titles_trimmed.csv` with `netflix_titles.csv`

Place `netflix_titles.csv` in the `data/` folder.

## What This App Does

This app allows users to explore a sample of Netflix titles with:

- Filters: Content type (All, Movie, TV Show)

- Minimum release year

- Rating (e.g., All, PG-13, TV-MA)

- Interactive Table: Displays filtered titles sorted by release year (newest first).

- Visualizations: Bar chart of content by release year and type.

- Pie chart of the top 10 genres.

- Bar chart of the top 10 countries producing content.

- Bar chart of rating distribution.

- Line chart of titles added over time (if date_added is available).

- Summary Stats: Shows counts of total titles, movies, TV shows, year range, and the top genre.

- Error Handling: Displays messages when no data is available for charts after filtering.

## How to Run Locally

1. Install Preswald: `pip install preswald`
2. Initialize a project: `preswald init netflix_explorer`
3. Place `netflix_titles.csv` in `netflix_explorer/data/`.
4. Copy `[data]` and content inside it from `preswald.toml` to your project's `preswald.toml` and `hello.py` into to your project's `hello.py`.
5. From `netflix_explorer` directory, Run: `preswald run`

## How to Deploy

1. Get your API key from [app.preswald.com](https://app.preswald.com) by creating your organization and creating API key inside it.
2. Deploy with: `preswald deploy --target structured --github <username> --api-key <key> hello.py`
