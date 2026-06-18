# NBA Player Analysis Dashboard

An interactive dashboard built with Preswald to analyze NBA player statistics including salary distributions and team comparisons.

## Dataset

This application uses NBA player data from the 2015-2016 season, containing information about:
- Player demographics (Name, Age, Height, Weight)
- Team affiliations
- College background
- Salary information
- Position

The data is stored in [data/nba.csv](data/nba.csv).

## Features

- Interactive age range filtering using dual sliders
- Scatter plot visualization of Age vs Salary, color-coded by team
- Line chart showing average salary by team
- Sortable and searchable data table with all player information

## Running Locally

1. Install dependencies:
```sh
pip install preswald
```

2. Run the application:
```sh
preswald run
```

The application will be available at http://localhost:8501

## Deployment

Deploy to Preswald Cloud:

```sh
preswald deploy
```

My application is available at https://my-project-119502-rxuxkdhr-ndjz2ws6la-ue.a.run.app
