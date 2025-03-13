# F1 Driver Analysis

App available at: [F1 Driver Analysis App](https://example-project-893477-emd4r6b4-ndjz2ws6la-ue.a.run.app/)

[Dataset link](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020)

This app looks at the following details about F1 drivers from years 1950 to 2024:

- Number of driver by their nationalities
- Numbers of drivers by the decade they were born


## Run the app

To run the app you can run the following command:

```
> preswarld run
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