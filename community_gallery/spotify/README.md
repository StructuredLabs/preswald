# Spotify Analysis

An interactive data exploration application that visualizes relationships between various attributes of songs released over the years from the Spotify dataset .

## Dataset

This application uses the Spotify songs dataset (referred to as 'songs_csv' in the code). This dataset contains information about songs including:

-   Popularity
-   Danceability
-   Tempo
-   Year of release
-   And other audio features

Data Source: https://www.kaggle.com/datasets/paradisejoy/top-hits-spotify-from-20002019

## Features

-   **Data Filtering**: View songs with popularity ratings above 85
-   **Interactive Year Selection**: Filter songs by year of release (1998-2020)
-   **Visualizations**:
    -   Scatter plot showing the relationship between popularity and danceability for songs from a selected year
    -   Scatter plot displaying the relationship between popularity and tempo across all songs

## Requirements

-   Python 3.7+
-   Preswald library
-   pandas
-   plotly

## Installation

1. Clone this repository:

    ```
    git clone https://github.com/StructuredLabs/preswald.git
    cd preswald/community_gallery/spotify
    ```

2. Install the required packages:

    ```
    pip install preswald pandas plotly
    ```

3. Ensure you have the Spotify dataset properly configured in `preswald.toml`.

## Usage

Run the application using:

```
preswald run
```

The application will display interactive visualizations in the Preswald interface

## Deployment

This application can be deployed using Preswald's deployment options:

1. **Local Deployment**: Run locally as described in the Usage section
2. **Cloud Deployment**: Follow Preswald's [documentation](https://docs.preswald.com) for cloud deployment options

    - Go to app.preswald.com
    - Create a New Organization (top left corner)
    - Navigate to Settings > API Keys
    - Generate and copy your Preswald API key
    - `preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py`

## Future Enhancements

-   Add more interactive filters (genre, artist, etc.)
-   Include correlation analysis between audio features
-   Add predictive modeling for song popularity

## Credits

-   [Kaggle](https://www.kaggle.com) for the Spotify data
-   [Preswald](https://www.preswald.com) for the visualization framework
