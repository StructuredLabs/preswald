This project is built using Preswald and includes various functionalities like data analysis, visualization, and interactivity. The goal is to deploy the project on Preswald for easy access and interaction.

Requirements

Before you run the project, ensure you have the following:
	•	Preswald CLI installed on your local machine. You can install it using the command:

pip install preswald


	•	A GitHub repository connected to Preswald (to deploy the project).
	•	An API Key for authentication (provided by Preswald).
	•	Python 3.x installed on your local machine.
	•	Your project files, including hello.py, .csv datasets, and other dependencies.

Setup Instructions

1. Clone the Repository (Optional)

If you haven’t already cloned the repository to your local machine, you can do it with the following command:

git clone https://github.com/your_username/your_repository_name.git
cd your_repository_name

2. Set Up Virtual Environment (Optional)

If you are using a virtual environment for your project, set it up as follows:

For macOS/Linux:

python3 -m venv venv
source venv/bin/activate

For Windows:

python -m venv venv
.\venv\Scripts\activate

3. Install Dependencies

Once the virtual environment is set up, install any required dependencies (if you have a requirements.txt):

pip install -r requirements.txt

4. Prepare Your Project Files

Ensure your project files are ready and placed in the appropriate structure. For example:
	•	hello.py: The main Python script for the project.
	•	FIFA21Complete.csv: The dataset file.

Ensure the code inside hello.py is working and includes logic such as creating plots or tables that you’d like to deploy on Preswald.

5. Authenticate with Preswald

If you don’t have your Preswald API key, sign up at Preswald and obtain your key. Once you have the key, run the following command to authenticate:

preswald login --api-key your_api_key

6. Deploy to Preswald

Once everything is set up, deploy your project using the Preswald CLI:

Deploy Your Project:

preswald deploy --target structured --github your_github_username --api-key your_api_key hello.py

	•	–target structured: Deploy the project as a structured app.
	•	–github your_github_username: Your GitHub username linked to the project.
	•	–api-key your_api_key: Your Preswald API key.

7. Access Your Project

Once deployed successfully, you will receive a URL to access the project. This will allow you to interact with your project on the Preswald platform.

8. Troubleshooting
	•	If you encounter any issues while deploying or running the app, check the error message carefully. Often, it might be an issue with missing dependencies, incorrect paths, or missing files.
	•	If the deployment fails with a 400 or SSL error, try ensuring your API key is correct and retry the deployment.

Example hello.py

Here’s an example of what your hello.py file might look like:

from preswald import text, plotly, table
import pandas as pd
import plotly.express as px

# Display initial texts
text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Attempt to load the CSV directly using pandas
file_path = 'FIFA21Complete.csv'  # Path to the CSV file

try:
    # Load the CSV data into a DataFrame
    df = pd.read_csv(file_path, delimiter=';')

    # Check if the DataFrame has been loaded successfully
    if df is not None:
        # Display information about the loaded data
        text(f"Dataset loaded successfully! Number of rows: {len(df)}")
        text(f"Columns: {', '.join(df.columns)}")

        # Show the first few rows of the dataset
        text(f"First few rows of the dataset:\n{df.head()}")

        # Create a scatter plot if necessary columns exist
        if all(col in df.columns for col in ['hits', 'potential', 'name']):
            fig = px.scatter(df, x='hits', y='potential', text='name',
                             title='Hits vs Potential',
                             labels={'hits': 'Hits', 'potential': 'Potential'})
            
            # Style the plot
            fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))
            fig.update_layout(template='plotly_white')

            # Show the plot
            plotly(fig)

            # Show the data in a table
            table(df)
        else:
            text("The dataset does not have the required columns: 'hits', 'potential', 'name'. Please check the data.")
    else:
        text("Failed to load the dataset. Please check the file path or format.")

except Exception as e:
    text(f"Error: {e}")

Conclusion

Your Preswald project is now set up and deployed. Feel free to update your project files, deploy new changes, and interact with your project directly on the Preswald platform!

