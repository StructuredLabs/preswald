# Methane Emissions Explorer

Methane Emissions Explorer is an interactive web application designed to visualize and analyze landfill methane emissions data. The application allows users to filter and explore emissions data, visualize trends, and understand the impact of different landfills on methane emissions.

## Features

- **Landfill Selection**: Users can select a landfill using the GHGRP ID.
- **Emission Uncertainty Filtering**: Apply a threshold filter to refine the dataset based on emission uncertainty.
- **Interactive Visualizations**:
  - **Emissions Map**: Visualize methane emission sources on a map.
  - **Uncertainty vs. Emission Rate Scatter Plot**: Analyze the relationship between uncertainty and emission rates.
  - **Emission Rate Distribution Histogram**: Understand the distribution of methane emissions.
  - **Emission Trends Over Time**: Track changes in emissions over time.

## How to Run the App

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`

1. **Install Dependencies**  
   Ensure you have Python installed along with the required packages. Install dependencies using:
   
   ```sh
   pip install preswald
   ```

2. **Run the Application Locally**  
   
   ```sh
   preswald  run
   ```
   
   This will start a local server where you can interact with the Methane Emissions Explorer.

## Deployment Instructions

### Deploy Your App to Structured Cloud

Once your app is running locally, deploy it using Preswald's structured cloud service.

### Steps to Deploy:

1. **Get an API Key**

   - Go to [Preswald](https://app.preswald.com)
   - Create a New Organization (top left corner)
   - Navigate to `Settings > API Keys`
   - Generate and copy your Preswald API key

2. **Deploy the App**  
   Run the following command in your terminal:

   ```sh
   preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
   ```

   Replace `<your-github-username>` and `<structured-api-key>` with your credentials.

3. **Verify the Deployment**  

   - After deployment, a live preview link will be provided.
   - Open the link in your browser to verify that the app is running correctly.

## Contributing

To add new features or improve the application, fork the repository, make changes, and submit a pull request.

## License

This project is released under an open-source license. Check the repository for details.
