# Spotify Energy vs. Danceability Analysis of Popular Songs

## Dataset

This data was sourced from [Spotify Music Dataset](https://www.kaggle.com/datasets/solomonameh/spotify-music-dataset) which contains popular and non-popular songs and their associated audio and descriptive features. I used the popular songs only to create this data analysis, and am limiting the popularity to a value of 50 or greater.

## About the App

This app attempts to find a connection between energy and danceability for highly popular songs -- testing the theory that the more popular a song is, the more danceable and high-energy it is. The results are somewhat conclusive, depending on the base number of songs included in the data analysis.

A slider was included to limit based on popularity, to be able to zoom in and see what highly-popular songs look like.

## Setup

1. Download the dataset listed above.
2. Clone Preswald locally from Github using your preferred method.
3. Create a virtualenv -- `pip -m venv .venv`
4. Ensure Preswald is installed -- `pip install preswald`
5. Ensure the data sources are correct in `preswald.toml`
6. Run `preswald run hello.py` in the main directory of this example.