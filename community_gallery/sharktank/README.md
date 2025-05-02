# Shark Tank Data Analysis App 

## Dataset Source  
This project analyzes **Shark Tank investment data**, containing details about:  
- Startups, industries, and entrepreneurs  
- Investment amounts, equity deals, and valuations  
- Sharks' participation and investment breakdowns  

 **Dataset Source:** [Shark Tank Investment Dataset](https://www.kaggle.com/datasets/thirumani/shark-tank-us-dataset data)  

---

## What the App Does  
This app provides an **interactive analysis** of Shark Tank investments. It allows users to:  
    Load and explore **Shark Tank investment data**  
    Filter startups based on **Total Deal Amount** using an interactive slider  
    Execute **SQL queries** to extract startups with investments greater than **$100,000**  
    Display **filtered data** in a structured table  
    Generate an **interactive scatter plot** comparing **Original Ask Amount vs. Total Deal Amount**  

---

## 🚀 How to Run & Deploy  
Follow these steps to set up, run, and deploy the app:

```bash
# Step 1: Install Preswald (if not already installed)
pip install preswald  

# Step 2: Configure your data sources  
nano preswald.toml  # Add database connection details  

# Step 3: Store sensitive credentials securely  
nano secrets.toml  # Add API keys and passwords  

# Step 4: Run the app  
preswald run hello.py  

# Step 5: Navigate to your project directory  
cd /path/to/project  

# Step 6: Deploy the app  
preswald deploy --target structured --github hetparikh2003 --api-key <your-api-key> hello.py  