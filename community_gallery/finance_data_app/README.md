# **My Finance Data App with Preswald**

This example demonstrates how to build an **interactive finance dashboard** using [Preswald](https://github.com/StructuredLabs/preswald). It displays Tesla (TSLA) stock prices, offers a **slider** to filter data by “Close” price, and showcases both **candlestick** and **scatter** charts.

## **Dataset Source**

- Data: [TSLA Historical Data]
- The CSV file (`TSLA.csv`) is located in the `data/` folder.

## **Project Structure**

```
my_finance_example/
├── README.md                 # This file
├── hello.py                  # Main Preswald script
├── data/
│   └── TSLA_stock_data.csv   # Example CSV (if included)
└── preswald.toml             # Maps 'my_finance_data' to the CSV
```

### **preswald.toml**

```toml
[data_sources.my_finance_data]
type = "csv"
path = "data/TSLA.csv"
```
  
- Ensures `get_df("my_finance_data")` references the Tesla CSV.

## **What Does This App Do?**

1. **Loads** Tesla stock data using Preswald’s `connect()` and `get_df()`.
2. **Filters** data above a chosen `Close` price threshold via a **slider**.
3. **Displays** a table of filtered rows.
4. **Plots**:
   - A **candlestick chart** for the last N rows (e.g., 20 or 10).
   - A **scatter** or **line** chart for the full dataset, colored by `Volume`.

## **How to Run Locally**

1. **Install Preswald (and optional Plotly)**:
   ```bash
   pip install preswald plotly
   ```
2. **Initialize or Navigate to the Project**:
   ```bash
   cd finance_data_app
   ```
3. **Run with Preswald**:
   ```bash
   preswald run hello.py
   ```
4. **Open the URL** that appears in your terminal (e.g. [http://localhost:8501](http://localhost:8501)).

## **Deployment Steps**

1. **Sign up** at [app.preswald.com](https://app.preswald.com/) to get an API key.
2. In your project folder:
   ```bash
   preswald deploy --target structured --github <your-username> --api-key <your-api-key> hello.py
   ```
3. **Check** the deployment link in your terminal to confirm the live app works.

## **Customization Ideas**

- Add more user input elements (e.g., date range filters).
- Compute and plot **moving averages** (e.g., 7-day or 30-day).
- Compare **multiple stocks** in a single dashboard.

## **Troubleshooting**

- Make sure you **run** via `preswald run hello.py`.
- Check your CSV **column names** match your code (case-sensitive).
- If the charts don’t appear, verify:
  - Plotly is installed.
  - `df` is **not empty** after filtering.
  - No spelling or case errors in `x`/`y` arguments to Plotly.

## **Resources**

- [Preswald Documentation](https://docs.preswald.com/)
- [Plotly for Python](https://plotly.com/python/)
- [Preswald GitHub](https://github.com/StructuredLabs/preswald)

---

**Enjoy exploring Tesla’s stock data with Preswald!**
