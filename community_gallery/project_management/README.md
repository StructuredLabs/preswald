# Project Preview

# Overview

The Project Management Dashboard is an interactive web application designed to help project managers and stakeholders visualize and analyze project data effectively. The dashboard provides insights into project budgets, statuses, and team sizes, allowing users to make informed decisions based on real-time data.

# Features

Data Visualization: The application uses Plotly to create interactive visualizations, including bar charts that display average budgets by project status.
Dynamic Filtering: Users can filter projects based on budget using a slider, allowing for a focused analysis of projects within specific budget ranges.
Data Summary: The dashboard summarizes key metrics, such as average budget and team size, grouped by project status (e.g., Completed, Ongoing, Cancelled).
User -Friendly Interface: The application features a clean and intuitive interface, making it easy for users to navigate and interact with the data.
Data Structure
The application expects a dataset in CSV format with the following columns:

# Attributes in the Dataset

ID: Unique identifier for each project.
Project_Name: Name of the project.
Start_Date: Start date of the project (format: YYYY-MM-DD).
End_Date: End date of the project (format: YYYY-MM-DD).
Status: Current status of the project (e.g., Completed, Ongoing, Cancelled).
Budget: Total budget allocated for the project.
Team_Size: Number of team members working on the project.
Technology: Technologies used in the project.
Client: Client associated with the project.
Location: Geographical location of the project.

# Example Visualisation

The dashboard generates a bar chart that displays the average budget for projects grouped by their status. 
The chart is interactive, allowing users to hover over bars to see detailed budget information.

# Running and Deployment

For running the application : preswald run
For deployment : preswald deploy --target structured --github <github username> --api-key <api-key> hello.py