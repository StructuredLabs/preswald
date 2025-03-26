# IMDB

## The dataset source.

The dataset used in this project is sourced from Kaggle:
[IMDB DataSet](https://www.kaggle.com/datasets/anandshaw2001/imdb-movies-and-tv-shows?resource=download). This project uses the **IMDb 2024 Movies & TV Shows** dataset, which includes essential details like **budget, revenue, genres, cast, ratings, and release dates**. The dataset provides insights into upcoming and released movies, enabling analysis of trends in film and television.

**Key Columns:**
- **Movie Name**: Title of the movie or TV show
- **Budget**: Estimated budget of the production
- **Revenue**: Box office revenue (if available)
- **Genres**: Categories associated with the movie (e.g., Drama, Action, Sci-Fi)
- **Overview**: A short synopsis of the movie
- **Cast**: List of lead actors/actresses
- **Original Language**: The primary language of the movie
- **Release Date**: The scheduled or actual release date
- **Vote Average**: IMDb user rating for the movie
- **Vote Count**: Number of votes the movie has received
- **Production Company**: The studio(s) behind the movie

## What your app does.

The **IMDb Explorer Dashboard** allows users to:
- **Filter movies by genre** (e.g., Drama, Action, Comedy)
- **Adjust rating thresholds** to see highly rated films
- **Vote Average vs. Vote Count** scatter plot, where you can visualize the relationship between a movie's Vote Average and the number of votes it has received.



## How to Run and Deploy the app
### Run
1. **Ensure Python 3.7+ is installed**
2. **Install dependencies**:
   ```bash
   pip install pandas plotly preswald
   ```
3. **Run the app locally**:
   ```bash
   preswald run
   ```

### Deploy
If the app is running successfully locally, you can deploy it using **Preswald’s deployment tools**.
- Deploy using:
    ```bash
    preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
    ```
- Replace `<your-github-username>` with your github username.
- Replace `<structured-api-key>` with your actual API key.

After deployment, you’ll receive a **live preview link** to share or access the app from any device.
---
