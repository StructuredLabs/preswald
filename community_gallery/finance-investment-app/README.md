# Preswald Project

# Finance Investment Analysis App

## Dataset
- **Source**: Manually provided finance dataset.
- **Description**: Data on individuals’ investment preferences, including demographics, investment avenues, and objectives.
- **Data Set Link**: https://www.kaggle.com/datasets/nitindatta/finance-data


## App Description
This app:
- Filters investors by age using a slider.
- Displays filtered data in a table (gender, age, Avenue, savings objectives).
- Shows a scatter plot of age vs Mutual Funds score, colored by gender.
- Bar plot: Average investment scores by gender

## How to Run the Application

### Prerequisites
Ensure that you have Python installed and the required dependencies installed. You will also need **Preswald** for running the interactive application.

### Installation Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd finance-investment-app
   ```

2. Install dependencies:
   ```bash
   pip install pandas plotly preswald
   ```

3. Run the application:
   ```bash
   preswald run
   ```

### Deploying the App in Preswald
The app can be deployed in **Preswald Structured Cloud** using the following steps:

1. **Get an API Key**
   - Go to [app.preswald.com](https://app.preswald.com)
   - Create a **New Organization** (top left corner)
   - Navigate to **Settings > API Keys**
   - Generate and copy your **Preswald API Key**

2. **Deploy Your App**
   Run the following command in your terminal, replacing `<your-github-username>` and `<structured-api-key>` with your actual credentials:
   ```bash
   preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
   ```

3. **Verify the Deployment**
   - Once deployment is complete, a **live preview link** will be provided.
   - Open the link in your browser and verify that your app is running.

### Live Demo
You can access the deployed application here:
[Finance Investment App](https://finance-investment-app-453589-ppj8yprb-ndjz2ws6la-ue.a.run.app)

## Notes
- Local execution requires `preswald run` (not `python hello.py`) to initialize the server.
