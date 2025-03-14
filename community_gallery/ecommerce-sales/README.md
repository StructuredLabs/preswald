📦 Preswald Project: E-commerce Sales Analysis
📊 Multi-Source Sales Dashboard with Filtering & Insights

📌 Overview
This project provides a data-driven dashboard for analyzing E-commerce sales trends across multiple datasets.
Using Preswald, we process three CSV files to generate key insights, financial calculations, and category-based filtering.

📂 Data Sources
We use three datasets in this project:

1️⃣ Amazon_Sale_Report.csv → Contains sales data from Amazon, including products, categories, and transaction details.
2️⃣ P_L_March_2021.csv → Profit and loss statement for March 2021, used for financial analysis.
3️⃣ Sale_Report.csv → General sales data from multiple sources, providing a broader view of transactions.

📂 All datasets are stored inside the data/ folder.

📊 Features
✔ Aggregated Sales Insights → Get sales summaries across multiple datasets.
✔ Category, State & Date Filtering → Analyze sales trends based on category, region, or custom date ranges.
✔ Profit & Loss Computation → Compare revenue vs. expenses for financial insights.
✔ Automated Data Processing → Reads CSV files, cleans data, and applies transformations.
✔ Export Processed Data → Save the cleaned and filtered reports for further use.

🛠️ How It Works
1️⃣ Loads Data → Reads Amazon_Sale_Report.csv, P_L_March_2021.csv, and Sale_Report.csv.
2️⃣ Cleans & Merges Data → Removes duplicates, fills missing values, and aligns columns.
3️⃣ Applies Filters → Users can filter sales by category, state, and time period.
4️⃣ Performs Calculations → Computes total sales, average order value, profit margins, and other KPIs.
5️⃣ Saves Processed Data → Results are exported for further analysis.

🚀 Running the Project
🔹 Prerequisites
Python 3.10
Preswald SDK
Required Libraries (install via requirements.txt)