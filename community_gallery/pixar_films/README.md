# Preswald Project

## Dataset
The dataset contains information about pixar films such as release dates, box office, and rotten tomato scores.

Dataset source: https://www.kaggle.com/datasets/willianoliveiragibin/pixar-films

## What the app does
1. This app displays a table displaying all films released on or after 2005. A threshold bar allows you to filter out films above a certain rotten tomato score.
2. This app also displays a plot of all films released on or after 2005 with their box office and rotten tomato scores.

## How to run locally
1. Under the `pixar_films` working directoy run the command `preswald run`.

## How to deploy
1. Under the `pixar_films` working directoy run the command `preswald deploy --target structured --github <your-github-username> --api-key <your-api-key> hello.py`.
2. A sample deployed version is available here: https://nba-152297-1iou9lla-ndjz2ws6la-ue.a.run.app/

