# Preswald Project

## Project URL
- [URL](https://esports-540993-tlmbhvcl-ndjz2ws6la-ue.a.run.app/)

## Setup
1. Install Preswald in a virtual environemnt.
2. Configure your data connections in `preswald.toml`
3. Add sensitive information (passwords, API keys) to `secrets.toml`
4. Run your app with `preswald run hello.py`

## Data source
- [Kaggle](https://www.kaggle.com/datasets/haseebindata/gaming-industry-trends-1000-rows)

## Deployment
1. Local
    ```bash
    preswald run

    # if docker is installed
    preswald deploy
    ```
2. Cloud(Structured)
    ```bash
    preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
    ```