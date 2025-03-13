# ☕ Coffee Sales Dashboard

Welcome to the **Coffee Sales Dashboard**! This interactive data visualization tool helps you analyze sales trends, product performance, and the impact of discounts in the coffee industry. The dashboard is built using **Preswald**, **Plotly**, and **SQL queries**, providing valuable insights into coffee sales data.

## 📊 Coffee Sales Data Explorer

You can access the live version of the app here: [Coffee Sales Analyzer](https://my-project-804057-1obtjchz-ndjz2ws6la-ue.a.run.app)

### Dataset Source

The dataset used in this project is derived from **global coffee sales data**. It includes various indicators related to coffee sales across different regions, including transaction volumes, revenue, discount impacts, and customer preferences from 2015 to 2023. This dataset allows for in-depth analysis and visualization of coffee sales trends across different markets and time periods. 

### App Features

The **Coffee Sales Data Explorer** offers interactive features for users to explore coffee sales data:

- **Sales Filter**: Users can filter sales data based on a **minimum sales threshold** using a slider, with a range from 500 to 2000 units.
  
- **Sales Analysis Visualizations**:
  - **Units Sold by City and Product**: A stacked bar chart comparing product sales by city.
  - **Average Sales by Product**: A bar chart displaying average sales for each product.
  - **Sales Amount vs Quantity**: A scatter plot showing the correlation between sales amount and quantity sold.
  - **Total Sales by City**: A bar chart visualizing total sales per city.

- **Sales Data Table**: An interactive table displaying filtered sales data, allowing users to sort and analyze high-sales records.

This app helps business owners, analysts, and managers optimize pricing, marketing, and product strategies based on data-driven trends.

## 🚀 How to Run the App Locally

### Prerequisites

1. **Install Python**: Ensure you have Python 3.7 or higher. Download it from [here](https://www.python.org/downloads/).

2. **Install Required Packages**: The app relies on the following Python libraries:
   - `pandas` for data manipulation
   - `plotly` for visualizations
   - `preswald` for app functionality
   

   To install the required packages, run the following command in your terminal:

   ```bash
   pip install pandas plotly preswald numpy

   ### Running the App

1. **Clone the repository** or download the necessary files.

2. **Ensure the dataset is available**: The dataset file `DatasetForCoffeeSales2.csv` should be placed in the `data` directory.

3. **Run the app with Preswald**: The application entry point is `hello.py`. Execute the following command to start the app locally:

   ```bash
   preswald run

