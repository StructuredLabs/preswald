# ⚽ Soccer Player Stats Explorer

## Table of Contents

1. [Folder Structure](#folder-structure)
2. [Dataset Source](#dataset-source)
3. [What the App Does](#what-the-app-does)
4. [Live Preview](#live-preview)
5. [How to Run Locally](#how-to-run-locally)

## Folder Structure

```
soccer_player_stats_explorer/
├── hello.py               (Main Preswald app script)
├── preswald.toml          (Project configuration)
├── secrets.toml           (Sensitive credentials)
├── data/                  (Datasets)
├── images/                (Logos)
├── README.md              (This file)
```

## Dataset Source

This app uses a 2022-2023 European Football Player Stats dataset, which includes detailed per-90-minute metrics (goals, assists, passes, tackles, etc.) for players across major European leagues. The dataset is available at:
https://www.kaggle.com/datasets/vivovinco/20222023-football-player-stats/data

## What the App Does

This app lets you filter by player names, position, age range, nationality, club, league, and then lets you choose one of several visualizations:

- Scatter Plot to compare any two numeric stats
- Correlation Heatmap to see how key metrics correlate
- Bar Chart to group and average a numeric stat by club, league, or nationality
- Histogram to display the distribution of any numeric stat

## Live Preview

Visit the live version of this app at:
[Live Preview Link](https://my-example-project-149428-0f40mhyw-ndjz2ws6la-ue.a.run.app/)

## How to Run Locally

To run the app in a virtual environment:

```
python3 -m venv venv
source venv/bin/activate
pip install preswald
```

Navigate to `community_gallery/soccer_player_stats_explorer`, then run:

```
preswald run
```
