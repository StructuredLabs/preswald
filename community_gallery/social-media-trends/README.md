# Social-Media Trends

Data sourced from [Kaggle](https://www.kaggle.com/datasets/atharvasoundankar/viral-social-media-trends-and-engagement-analysis).

The real dataset is dynamically filtered using custom SQL query to retrieve relevant filtered data. This app offers custom data visualizations that empower users to gain insights through Shares-Based Analysis(User Control), Engagement-Based Analysis, & Region-Based Analysis. 

To run this example:
- `pip install preswald` (If you dont already have Preswald installed)
- `git clone https://github.com/StructuredLabs/preswald.git`
- `cd preswald/examples/social-media-trends/`
- `preswald run`

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`

## Deploy
Deploy Your App to Structured Cloud
Once your app is running locally, deploy it.

Get an API key

Go to app.preswald.com
Create a New Organization (top left corner)
Navigate to Settings > API Keys
Generate and copy your Preswald API key
Deploy your app using the following command:

preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py

Replace <your-github-username> and <structured-api-key> with your credentials.

Verify the deployment

Once deployment is complete, a live preview link will be provided.
Open the link in your browser and verify that your app is running.