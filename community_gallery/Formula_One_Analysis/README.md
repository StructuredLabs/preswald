
# Preswald F1 Analytics Dashboard

## About

An interactive F1 dashboard built using **Preswald** to analyze driver and constructor performance.

### Dataset Source:
- The dataset is saved in the `/data` folder as `full_results_with_names.csv`.
- [Kaggle Dataset Link](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020/data)

The dataset was created by **combining 3 CSV files**:
- `results.csv`
- `drivers.csv`
- `constructors.csv`

### Features:
- Driver grid vs. final position (2024)
- Fastest lap speeds filtered by year and speed
- Driver points over the years
- Constructor wins over selected years
- Race wins by driver
- Top 15 drivers by total points

## Setup

1. **Configure data** in `preswald.toml`:
```toml
[data.full_results_with_names]
type = "csv"
path = "/path/to/full_results_with_names.csv"
```
2. Add any secrets (if needed) to `secrets.toml`.

3. Run the app locally:
```bash
preswald run
```
**Note:** If you created a new file (e.g., `test.py`), update `preswald.toml`:
```toml
[project]
title = "Preswald Project"
version = "0.1.0"
port = 8501
slug = "my-example-project-678312"  # Required: Unique identifier for your project
entrypoint = "test.py"              # Name of your main script
```


## Deployment

1. **Get an API key:**
- Go to [app.preswald.com](app.preswald.com)
- Create a New Organization (top left corner)
- Navigate to Settings > API Keys
- Generate and copy your Preswald API key

2. **Deploy the app:**
```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```
 Replace `<your-github-username>` and `<structured-api-key>` with your actual GitHub username and API key.


## Live App

[Click here to view the app](https://my-example-project-678312-u7yqofkh-ndjz2ws6la-ue.a.run.app)
