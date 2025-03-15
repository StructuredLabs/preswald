# Kerala Rainfall Analysis - 2022

Kerala Rainfall Analysis - 2022 is an interactive web application designed to visualize and analyze the monthly and seasonal rainfall data of various met-run stations in Kerala, India for the year 2022. The application enables users to filter data based on rainfall thresholds, select locations to view monthly rainfall trends, and explore seasonal rainfall patterns across multiple stations.

## Features

- **Location Selection:** Users can select a location to visualize its monthly rainfall.
- **Rainfall Threshold Filtering:** Apply threshold filters to refine the dataset based on annual, summer, South West Monsoon, and North East Monsoon rainfall.
- **Interactive Visualizations:**
  - **Monthly Rainfall Bar Chart:** View monthly rainfall distribution for selected locations.
  - **Annual Rainfall Comparison:** Compare annual rainfall across different locations.
  - **Seasonal Rainfall Trends:** Explore rainfall trends during Summer, South West Monsoon, and North East Monsoon seasons.
- **Dynamic Data View:** Filter and view the dataset dynamically based on rainfall thresholds.

## How to Run the App

### Setup

1. Configure your data connections in `preswald.toml`.
2. Add sensitive information (passwords, API keys) to `secrets.toml`.

### Install Dependencies

Ensure you have Python installed along with the required packages. Install dependencies using:

```bash
pip install preswald pandas plotly
```

### Run the Application Locally

```bash
preswald run
```

This will start a local server where you can interact with the Kerala Rainfall Analysis.

## Deployment Instructions

### Deploy Your App to Structured Cloud

Once your app is running locally, deploy it using Preswald's structured cloud service.

#### Steps to Deploy:

1. **Get an API Key**

   - Go to [Preswald](https://preswald.com)
   - Create a New Organization (top left corner)
   - Navigate to Settings > API Keys
   - Generate and copy your Preswald API key

2. **Deploy the App** Run the following command in your terminal:

```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```

Replace `<your-github-username>` and `<structured-api-key>` with your credentials.

3. **Verify the Deployment** After deployment, a live preview link will be provided. Open the link in your browser to verify that the app is running correctly.

## Contributing

To add new features or improve the application, fork the repository, make changes, and submit a pull request.

## License

This project is released under an open-source license. Check the repository for details.

