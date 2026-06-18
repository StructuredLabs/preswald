# 🚗 Car Data Dashboard

An interactive dashboard to explore car data using **Preswald**, **Plotly**, and dynamic SQL filtering. This project allows users to analyze car brands, colors, and price insights through filters and rich visualizations.

---

## 📊 Features

- Dropdown filters:
  - Car Brand
  - Car Color
- Slider for Price Threshold
- Dynamic SQL query generation based on filter selection
- Interactive Bar Chart:
  - Color vs Price for a selected car brand
  - Brand vs Total Price if "All" brands are selected
- Pie Chart showing Color Distribution
- Filtered results displayed in an interactive table

---

## 📁 Dataset Columns

| Column | Description              |
|--------|--------------------------|
| `name` | Car Brand/Model Name     |
| `color`| Car Color                |
| `value`| Car Price (in USD)       |

---

## ✅ How to Use the Dashboard

1. **Select Filters:**
   - Choose a **Car Brand** or select `"All"` to see all brands.
   - Choose a **Car Color** or select `"All"` to see all colors.
   - Adjust the **Price Threshold slider** to filter by price.

2. **View Outputs:**
   - **Table**: Shows filtered car data.
   - **Bar Chart**:
     - If a car brand is selected → `Color vs Price`
     - If "All" is selected → `Brand vs Total Price`
   - **Pie Chart**: Distribution of selected car colors.

3. **No Results Handling**:
   - If no matching records, you’ll see: `"No data available for the selected filters."`

---

## 🚀 Getting Started

### 📦 1. Install Preswald
Make sure you have Python installed, then run:

```bash
pip install preswald
▶️  Run the Dashboard
preswald run


Checkout deployed app at : https://preswald-assessment-317498-4axklqub-ndjz2ws6la-ue.a.run.app

📌 Requirements
Python 3.7+
Preswald
Plotly
Pandas

If you want to change dataset, make sure you also change it in preswald.toml