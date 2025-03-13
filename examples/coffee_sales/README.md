<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: auto;
        }
        h1, h2, h3 {
            color: #333;
        }
        code {
            background: #f4f4f4;
            padding: 5px;
            border-radius: 4px;
        }
        pre {
            background: #f4f4f4;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
        img {
            max-width: 100%;
        }
        .container {
            padding: 20px;
        }
        ul {
            margin-left: 20px;
        }
        li {
            margin-bottom: 10px;
        }
        hr {
            border: 1px solid #ccc;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>☕ Sales Dashboard</h1>

    <img src="https://my-project-804057-1obtjchz-ndjz2ws6la-ue.a.run.app" alt="Dashboard Banner">

    <p>Welcome to the <strong>Sales Dashboard</strong>! This interactive visualization tool helps analyze sales trends, product performance, and the impact of discounts in the coffee industry. Built using <strong>Preswald</strong>, <strong>Plotly</strong>, and <strong>SQL queries</strong>, this dashboard provides valuable insights into sales data.</p>
    <hr>

    <h1>☕ Coffee Sales Data Explorer</h1>

    <p>Find the app here- <a href="https://my-project-804057-1obtjchz-ndjz2ws6la-ue.a.run.app" target="_blank">Coffee Sales Analyzer</a></p>

    <h2>Dataset Source</h2>

    <p>The dataset used in this project is derived from <strong>global coffee sales data</strong>. It includes various indicators related to coffee sales across different regions, including transaction volumes, revenue, discount impacts, and customer preferences from 2015 to 2023. This dataset allows for in-depth analysis and visualization of coffee sales trends across different markets and time periods.</p>

    <p>The dataset is essential for analyzing coffee sales patterns, understanding customer preferences, and optimizing pricing and discount strategies.</p>

    <h2>What Does the App Do?</h2>

    <p>The <strong>Coffee Sales Data Explorer</strong> is an interactive dashboard that visualizes and analyzes global coffee sales trends. The app provides an in-depth look at sales performance across various dimensions and offers multiple interactive features to help users make data-driven decisions:</p>

    <ul>
        <li><strong>Sales Filter</strong>:  
            The app allows users to filter sales data based on a <strong>minimum sales threshold</strong>. A slider lets users adjust the minimum sales amount, ranging from 500 to 2000 units, to view data for transactions that meet or exceed the selected threshold.
        </li>
        <li><strong>Sales Analysis Visualizations</strong>:
            <ul>
                <li><strong>Units Sold by City and Product</strong>: A stacked bar chart visualizes the total quantity of coffee products sold by city and product type. This chart helps compare how different products perform across various cities.</li>
                <li><strong>Average Sales by Product</strong>: A bar chart displays the <strong>average sales</strong> for each product, showing which products are the most profitable on average.</li>
                <li><strong>Sales Amount vs Quantity</strong>: A scatter plot reveals the relationship between final sales amount and quantity sold for each product, showing how sales volumes correlate with revenue.</li>
                <li><strong>Total Sales by City</strong>: A bar chart presents the <strong>total sales by city</strong>, allowing users to identify the regions contributing most to overall sales.</li>
            </ul>
        </li>
        <li><strong>Sales Data Table</strong>:  
            The app features an interactive table that displays filtered sales data. Users can browse high-sales records, sort, and filter data for more in-depth analysis.
        </li>
    </ul>

    <p>This app provides valuable insights into sales patterns, helping business owners, analysts, and managers optimize pricing, marketing, and product strategies based on data-driven trends.</p>

    <h2>How to Run the App Locally</h2>

    <h3>Prerequisites</h3>

    <ol>
        <li><strong>Install Python</strong>: Ensure you have Python 3.7 or higher installed. You can download Python from <a href="https://www.python.org/downloads/" target="_blank">here</a>.</li>
        <li><strong>Install Required Packages</strong>: The project relies on the following Python libraries:
            <ul>
                <li><code>pandas</code> for data manipulation</li>
                <li><code>plotly</code> for visualizations</li>
                <code><strong>preswald</strong> for app functionality</code>
                <li><code>numpy</code> for numerical operations</li>
            </ul>
            To install the required packages, run the following command in your terminal:
            <pre><code>pip install pandas plotly preswald numpy</code></pre>
        </li>
    </ol>

    <h3>Running the App</h3>

    <ol>
        <li><strong>Clone the repository</strong> or download the necessary files.</li>
        <li><strong>Ensure the Dataset is Available</strong>: The data file <code>DatasetForCoffeeSales2.csv</code> should be in the <code>data</code> directory.</li>
        <li><strong>Run the App with Preswald</strong>: The application entry point is set to <code>hello.py</code>. Execute the following command to start the app locally:
            <pre><code>preswald run</code></pre>
            The app will launch on port <strong>8501</strong>, and you can access it at the provided local URL.
        </li>
    </ol>

    <h2>Additional Notes</h2>

    <ul>
        <li>This dataset provides rich insights into coffee sales trends, customer preferences, and discount strategies.</li>
        <li>Consider enhancing the app with additional features such as:
            <ul>
                <li>Forecasting future coffee sales based on historical trends</li>
                <li>Correlation analysis between discount rates and sales growth</li>
                <li>Customer segmentation to tailor marketing strategies</li>
                <li>Seasonal trends in coffee sales based on weather patterns</li>
            </ul>
        </li>
        <li>Regular updates to the dataset will ensure the most current sales data is available for analysis.</li>
    </ul>

    <p>Explore coffee sales trends and optimize your business strategies with this interactive and insightful dashboard!</p>

</div>

</body>
</html>
