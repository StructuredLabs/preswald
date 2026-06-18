# Spotify Streams Analysis

This app analyzes the most streamed songs on Spotify in 2024. It provides insights into top artists, tracks, and trends using interactive visualizations.

## Dataset Source
The dataset used in this app contains information about Spotify streams, YouTube views, and other metrics for popular tracks.  
- **File**: `data/Most_Streamed_Spotify_Songs_2024_utf8.csv`

## What the App Does
The app includes:
- A bar chart showing the top artists by Spotify streams.
- A scatter plot comparing Spotify streams vs YouTube views.
- A slider to filter songs based on stream counts.
- Key metrics like total streams, total tracks, and the top-performing track.

## How to Run the App
1. Clone this repository:
   ```bash
   git clone https://github.com/<your-github-username>/Preswald.git
   cd Preswald/community_gallery/spotify_streams_analysis
Install dependencies:
bash
Copy
1
pip install preswald
Run the app locally:
bash
Copy
1
preswald run hello.py
 How to Deploy the App

To deploy the app to Structured Cloud:
Install Preswald:
bash
Copy
1
pip install preswald
Deploy the app:
bash
Copy
1
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py


