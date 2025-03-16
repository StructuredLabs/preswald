# Motor Vehicle Collisions Explorer

An interactive Preswald app to explore NYC Motor Vehicle Collision data, focusing on person-level information.

## Dataset Source

The Motor Vehicle Collisions dataset is provided by the New York City Police Department (NYPD) and contains information about all traffic crashes in NYC. This specific dataset focuses on the person-level information for each collision, including details about the individuals involved, their injuries, and demographic information.


## Data Cleaning

The app performs several data cleaning steps to ensure the visualizations are accurate and meaningful:

1. Converting date fields to proper datetime format
2. Converting age values to numeric and filtering out invalid ages
3. Standardizing gender, person type, and injury status values
4. Handling missing values appropriately

## App Features

This app provides five interactive visualizations to explore the NYC Motor Vehicle Collisions data:

1. **Injury Statistics by Person Type** - Bar chart showing injury outcomes across different person types (occupants, pedestrians, etc.)
2. **Age Distribution of Involved Persons** - Histogram showing the age distribution of people involved in collisions, broken down by person type
3. **Gender Distribution by Person Type** - Grouped bar chart comparing gender distribution across different person types
4. **Collisions by Time of Day** - Line chart showing the frequency of collisions throughout the day
5. **Safety Equipment Usage and Injury Outcomes** - Bar chart analyzing the relationship between safety equipment usage and injury severity

The app also provides a data sample table to explore the raw data.

## How to Run

1. Install Preswald:
   ```
   pip install preswald
   ```

2. Clone this repository and navigate to the project directory

3. Run the app:
   ```
   preswald run
   ```

## How to Deploy

To deploy this app to Structured Cloud:

1. Get an API key from [app.preswald.com](https://app.preswald.com/)
2. Deploy using the following command:
   ```
   preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
   ```

## Live Demo

[Link to the deployed app will be added after deployment]
