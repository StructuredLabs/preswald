# SF Salaries Explorer App

## Dataset Source
This application utilizes the SF Salaries Dataset available on Kaggle. You can find the dataset [here](https://www.kaggle.com/datasets/kaggle/sf-salaries).

## About the App
The SF Salaries Explorer App is designed to analyze and visualize salary data from San Francisco city employees. The app explores trends in compensation, overtime pay, and employee benefits over the years. Users can interact with the data through dynamic visualizations and custom filters, gaining insights into pay distributions, the impact of benefits, and changes in total pay over time.

## How to Run and Deploy the App

### Setup
1. **Configure Data Connections:**
   - Ensure that your data connections are correctly configured in `preswald.toml`.

2. **Add Sensitive Information:**
   - Place any sensitive information such as passwords and API keys into `secrets.toml`.

3. **Run the App:**
   - Execute your application by running `preswald run` from your terminal.

### Preprocessing Data
The data is preprocessed to ensure accuracy and usability within the app. This includes:
- Converting pay columns to numeric types and handling missing values.
- Filtering and cleaning the dataset to remove anomalies or incorrect data entries.
- Standardizing job titles and filling missing categorical information.

### Features
- **Dynamic Data Views:** Interact with the data through sliders and filters to view specific subsets of the data.
- **Visual Trends Analysis:** Explore various visualizations that depict trends and distributions in the dataset, such as average total pay over time, the distribution of pay components, and correlations between base pay and overtime pay.

### Deploy Your App to Structured Cloud

#### Deployment Steps
To deploy your SF Salaries Explorer App to the Structured Cloud, follow these steps:

1. **Get an API Key:**
   - Visit [Preswald Platform](https://app.preswald.com).
   - Create a new organization by selecting "Create New Organization" in the top left corner.
   - Navigate to `Settings > API Keys`.
   - Click on "Generate" to create a new API key and copy it.

2. **Deploy Your App:**
   - Open your terminal and deploy your app using the command below:
     ```
     preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
     ```
   - Replace `<your-github-username>` and `<structured-api-key>` with your actual GitHub username and the Preswald API key you obtained.

#### Verify the Deployment
- Once the deployment process is complete, you will receive a live preview link.
- Open this link in your browser to verify that your app is running as expected on Structured Cloud.

By following these steps, your application will be hosted on Structured Cloud, making it accessible via the internet. Check your deployment and ensure all functionalities are working correctly.


## Key Insights from the App
- The average total compensation for city employees indicates variations over the years, reflecting economic and policy changes.
- Benefits are a significant part of the total compensation, highlighting their importance in the overall remuneration package for city employees.

Explore the app to discover more insights and understand the complexities of salary data in San Francisco city employment.
