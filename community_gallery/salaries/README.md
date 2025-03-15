# Preswald Project

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`

Salary Insights Visualization App

📊 Dataset Source

The dataset used in this app, Salaries, is sourced from Kaggle. It includes salary information across various job roles, experience levels, and companies.

🚀 App Features

This Preswald application offers interactive visualizations to explore salary patterns within the dataset:

Salary Distribution by Experience Level: Visualize salary trends across different experience categories.

Top 10 Salaries by Job Titles: Identify the job titles offering the highest median salaries.

Salary Distribution by Company Size: Understand how salaries differ among small, medium, and large companies.

Relationship between Salary and Remote Work Ratio: Explore how remote work impacts salaries.

⚙️ Installation and Local Setup

1. Install Preswald CLI

If you haven't already installed Preswald CLI, do so by running:

pip install preswald

2. Run Your App Locally

Launch your app locally using:

preswald run

Your app will be available at http://localhost:8000.

🚀 Deploying Your App

To deploy your application to Preswald Cloud:

Authenticate with Preswald:

Visit app.preswald.com.

Authenticate using GitHub.

Create an organization and generate an API key.

Deploy the App:
Deploy your application to Preswald Cloud with the command:

preswald deploy --target structured

On your first deployment, you'll be asked for your GitHub username and Preswald API key.

Enjoy visualizing your salary insights! 📈🎉