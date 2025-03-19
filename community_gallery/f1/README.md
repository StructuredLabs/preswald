# Preswald Project

App available here: [F1 Data Analysis](https://preswald-app-f1-new-598598-1063538583924.us-west1.run.app/)
[Dataset Link](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020?resource=download&select=qualifying.csv)

## Dataset
The dataset consists of all information on the Formula 1 races, drivers, constructors, qualifying, circuits, lap times, pit stops, championships from 1950 till the latest 2024 season. I chose to do analysis on 2021 data as it was the most intense season with 2 drivers tied in points headed into the final race. The ending was controversial, so I wanted to do some data visualization and see how they were performing throughout the season.

## My App
My app has 4 sections:
- Individual driver points progression as the season went on
- The number of Constructors Championships teams Alpine, McLaren, Mercedes, and Red Bull have won
- McLaren driver Lando Norris's individual race finishes for the season
- Head-To-Head comparison of drivers on teams Mercedes, Red Bull, and Ferrari

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`
4. To Deploy run `preswald deploy --target gcp`

I had trouble deploying to Structured (I opened an issue [here](https://github.com/StructuredLabs/preswald/issues/438)) so I deployed to GCP instead.