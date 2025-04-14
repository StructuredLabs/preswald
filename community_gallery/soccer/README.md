# Soccer Data Analysis

App available at: [Soccer Data Analysis App](https://soccer-311433-kruu1k6k.preswald.app/)

[Dataset link](https://www.kaggle.com/datasets/cihan063/soccer-players)

This app analyzes soccer data from various leagues and provides insights such as:
- Most popular teams in different countries.
- Player performance over the years.
- League rankings and team statistics.

## Run the app

To run the app locally, use the following command:

```
preswald run
```

## Deploy the app

To deploy this app, create a preswald API key:
- go to [preswald.com](preswald.com)
- Create a New Organization (top left corner)
- Navigate to Settings > API Keys
- Generate and copy your Preswald API key

Add your Github username and Preswald API key in the following command:

```
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```

