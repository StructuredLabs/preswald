# World Happiness Report App

## Dataset
- **Source:** [Kaggle - World Happiness Report 2021](https://www.kaggle.com/datasets/ajaypalsinghlo/world-happiness-report-2021)
- **Columns:** Country, Happiness Score, GDP per Capita, Social Support, Life Expectancy, etc.

## About This App
This app allows users to:
- Filter countries based on happiness score.
- Visualize the correlation between GDP and Happiness.
- Interactively explore the dataset.

## How to Run
1. Install Preswald: `pip install preswald`
2. Initialize project: `preswald init my_example_project && cd my_example_project`
3. Place `world_happiness.csv` in `data/`
4. Run `hello.py` locally: `preswald run`
5. Deploy using: `preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py`

## Demo

https://world-happiness-709242-bmuvr4gg-ndjz2ws6la-ue.a.run.app/


