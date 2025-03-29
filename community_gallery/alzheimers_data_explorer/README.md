# Alzheimer's Disease Data Explorer 🧠

## Dataset Source
- **Dataset Name:** [Alzheimer's Disease Dataset](https://www.kaggle.com/datasets/rabieelkharoua/alzheimers-disease-dataset)
- **Description:** Contains medical records of patients with and without Alzheimer's, including cognitive scores, behavioral problems, and cholesterol levels.

## Live Demo
Access the live demo at: [https://my-example-project-587146-egykqrxv.preswald.app/](https://my-example-project-587146-egykqrxv.preswald.app/)

## What This App Does
The Alzheimer's Disease Data Explorer is an interactive dashboard that helps visualize and analyze Alzheimer's disease-related patient data. Key features include:

1. **MMSE Score Analysis**: Visualize the distribution of Mini-Mental State Examination scores across patients
2. **Age vs. Cholesterol Correlation**: Explore the relationship between age and cholesterol levels for different diagnosis types
3. **Interactive Filtering**: Use a slider to filter patients by MMSE Score threshold
4. **Behavioral Analysis**: View behavioral problem patterns across different diagnosis types
5. **Patient Data Table**: Access filtered patient data with key metrics for clinical or research insights

## How to Run and Deploy

### Local Setup
1. Install the required dependencies:
   ```bash
   pip install preswald plotly
   ```

2. Run the application locally:
   ```bash
   python hello.py
   ```

3. Open your browser and navigate to the local development server URL

### Deploy Your App to Structured Cloud
Once your app is running locally, deploy it:

1. Get an API key:
   - Go to [app.preswald.com](https://app.preswald.com)
   - Create a New Organization (top left corner)
   - Navigate to Settings > API Keys
   - Generate and copy your Preswald API key

2. Deploy using the command:
   ```bash
   preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
   ```
   Replace `<your-github-username>` and `<structured-api-key>` with your credentials. 
   Note: your github username must be all lowercase.
