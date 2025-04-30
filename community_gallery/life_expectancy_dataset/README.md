# Life Expectancy Data Analysis

App available at: [Life Expectancy Data Analysis App](https://preswald-life-expectancy-dataset-438596-qzdwxeax-ndjz2ws6la-ue.a.run.app/)

[Dataset link](https://www.kaggle.com/datasets/fredericksalazar/life-expectancy-1960-to-present-global)

This app looks at the following details about Life Expectancy from years 1960 to 2024:

- First table presents all the data from 1998 to 2000 from the region `ASIA`
- Second table presents a dynamic data view from 1990 to 2000 
- The scatter plot is a plot of `life_expectancy_men_min` over the years


## Run the app

To run the app you can run the following command:

```
> preswarld run
```

## Deploy the app

To deploy this app, create a preswald API key:
- go to [api.preswald.com](api.preswald.com)
- Create a New Organization (top left corner)
- Navigate to Settings > API Keys
- Generate and copy your Preswald API key

Add your Github username and Preswald API key in the following command:

```
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```
