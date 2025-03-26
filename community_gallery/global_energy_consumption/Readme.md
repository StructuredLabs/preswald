Global Energy Consumption Analysis
Welcome to my app, I had built these app using Preswald, allowing users to see the Global Energy Consumption Visualizations!


## Dataset source
I had used the Dataset in this app from Kaggle!
Here is the link for the dataset https://www.kaggle.com/datasets/atharvasoundankar/global-energy-consumption-2000-2024

The dataset used in this app contains Global Energy Consumption over the years. It includes details like:
**Country**
**Year**
**Total Energy Consumption**
**Carbon Emission(Million tons)**

## How does this app work?
**pip install pandas plotly preswald**
**preswald run hello.py**

## What does this app do?
**First we load the dataset from global_energy_consumption.csv**
**After that we created a interactive slider to choose Year**
Users can select a year between 2000 and 2024 using a slider the selected year is converted into an integer for filtering.

**Query the dataset based on Selected Year**
Sql query fetched energy consumption data for that selected year.

**Display the filtered data in a table**

**Interactive Scatter Plot**
Here Xaxis is Country, while Y-axis is Total Energy Consumption, differentiate the data points by Country name

Increases marker size and adds light blue color.

**Displays the scatter plot**
Displays the scatter plot in the app.
