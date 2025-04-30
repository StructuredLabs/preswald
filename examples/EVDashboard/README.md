# EV Analytics Dashboard

## Dataset Source
The dataset used for this project is sourced from [Electric Vehicle Population Data](https://catalog.data.gov/dataset/electric-vehicle-population-data). This dataset contains information on electric vehicles registered in the United States, including their make, model, electric range, and location.

## About the App
The EV Analytics Dashboard provides insights into electric vehicle registrations, distribution, and trends in the United States. The app offers interactive visualizations, including:
- A histogram of EV registrations over time.
- A pie chart showing the distribution of EV types.
- A bar chart of popular EV manufacturers.
- A histogram for electric range distribution.
- A map visualizing EV locations in the USA.

Users can filter the data using a slider to select a minimum electric range, refining the displayed insights.

## How to Run the App Locally
1. Install [Preswald](https://preswald.com/) if you haven't already.
2. Run the following command to start the app locally:
   ```sh
   preswald run
   ```
3. The dashboard will be available at a local URL where you can explore the data interactively.

## How to Deploy the App
### 1. Get an API Key
1. Go to [Preswald](https://app.preswald.com/).
2. Create a New Organization (top left corner).
3. Navigate to **Settings > API Keys**.
4. Generate and copy your Preswald API key.

### 2. Deploy the App
Run the following command, replacing placeholders with your credentials:
```sh
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```

### 3. Verify the Deployment
Once deployment is complete, a live preview link will be provided. Open the link in your browser to verify that the app is running as expected.

Enjoy exploring the EV Analytics Dashboard! 🚗⚡

