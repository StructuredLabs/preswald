# Preswald Project
# Chocolate Sales Analysis  

## 📌 Overview  
This project provides an interactive data analysis app for **Chocolate Sales Data**, built using **Preswald**.  
It allows users to manipulate and visualize sales data dynamically using filters and visualizations.

## 📊 Dataset  
**Source**: https://www.kaggle.com/datasets/atharvasoundankar/chocolate-sales?resource=download



## 🛠 Features  
✅ Displays the first 15 records of the dataset.  
✅ Allows dynamic filtering using a **slider** (filters data based on sales amount).  
✅ Predefined SQL-like filters (e.g., filtering by product type or sales amount).  
✅ Various visualizations including **scatter plots, bar charts, and box plots**.  

## 📂 Folder Structure  
## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run`

## 🚀 How to Run  
1. **Set up your environment**  
   - Install **Preswald** if not already installed:  
     ```bash
     pip install preswald
     ```
   - Clone the repository:
     ```bash
     git clone https://github.com/your-repo-name.git
     cd examples/chocolate_sales_example/
     ```

2. **Run the App Locally**  
   ```bash
   preswald run chocolate_sales.py

	•	Open the provided localhost link in your browser.

3.	**Deploy to Structured Cloud**
	•	Get your Preswald API Key from Preswald Settings.
	•	Deploy using: preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> chocolate_sales.py

### **Customizations**:
- Replace **`your-repo-name`** with your actual **GitHub repository name**.
- Replace **`your-username`** with your **GitHub username**.


