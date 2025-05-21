Electric Vehicle Data Explorer

This app shows total vehicles and average electric range. It lets you filter data by model year. You can see a scatter plot and a table of the filtered data.

Dataset Source

This data comes from a public dataset of electric vehicles on Kaggle.

How to Run

Open a terminal and go to the folder with the preswald.toml file.
Run:
preswald run
Open the local link in your browser. You will see the app.

How to Deploy
Go to app.preswald.com.
Create an organization.
Go to Settings and make a new API key.
Run:
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
Change <your-github-username> and <structured-api-key> to your actual values.

Files
hello.py: Main script for the app.
data/Electric_Vehicle_Population_Data_small.csv: The smaller CSV file with sample data (the original data was too big).