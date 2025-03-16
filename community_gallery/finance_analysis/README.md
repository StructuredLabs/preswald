
# 📊 Finance Data Analysis App - Preswald Assessment

Welcome to the **Finance Data Analysis App** built using **Preswald**!  
This project demonstrates basic data manipulation, visualization, and interactive UI components.

---

## 🚀 Features Implemented:

### 1. **Data Loading**
- Loaded the CSV file `Finance_data.csv` from the `data/` folder.
- Displayed the entire dataset in a table format.

### 2. **Filtered data based on gender using SQL**
- Filtered data based on gender using SQL query:
  sql
  SELECT * FROM Finance_data WHERE gender = 'Male'
### 3. **Sorted data by a specific column**
Sorted the dataset based on Fixed_Deposits column in descending order
SELECT * FROM Finance_data ORDER BY Fixed_Deposits DESC
### 4. **Used a slider to dynamically filter data**
Implemented an interactive slider to filter rows dynamically
threshold = slider("Threshold for Mutual Funds", min_val=0, max_val=10, default=5)
filtered_slider_df = df[df["Mutual_Funds"] > threshold]
### 5. **Created a basic scatter plot visualization**
Created a scatter plot to visualize the relationship between Fixed_Deposits and Mutual_Funds using Plotly:
fig = px.scatter(df, x="Fixed_Deposits", y="Mutual_Funds", title="Fixed Deposits vs Mutual Funds")
plotly(fig)


## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`
