# **Employee Well-being Analysis - Preswald App**  

## **Overview**  
This **Preswald-powered web app** analyzes the effects of remote work on **employee mental health**. It allows users to explore **stress levels, work hours, and job satisfaction** using interactive tables and visualizations.  

## **Dataset**  
- **Source:** [Kaggle - Remote Work and Mental Health](https://www.kaggle.com/datasets/waqi786/remote-work-and-mental-health/data)  
- **Description:**  
  This dataset contains survey responses on how remote work affects employees’ stress levels, work-life balance, and job satisfaction.  
- **File format:** CSV (`Impact_of_Remote_Work_on_Mental_Health.csv`)  

## **Features**  
✔ **Filter employees with high stress levels**  
✔ **Interactive slider** to analyze work hours  
✔ **Dynamic tables** for exploring data  
✔ **Scatter plot visualization** of **work hours vs. employee age**  
✔ **Deployable on Structured Cloud**  

## **Installation & Setup**  

### **1. Install Preswald**  
Ensure you have Python installed, then run:  
```bash
pip install preswald
```

### **2. Clone the Repository**  
```bash
git clone https://github.com/StructuredLabs/preswald.git
cd preswald/community_gallery/Employee_well_being_analysis
```

### **3. Run the App Locally**  
```bash
preswald run hello.py
```

---

## **Implementation Details**  

### **1. Load the Dataset**  
The dataset is loaded from **Preswald’s database connection**.  
```python
from preswald import connect, get_df

connect()  # Connects to preswald.toml data sources
df = get_df("Impact_of_Remote_Work_on_Mental_Health_csv")  # Load dataset
```

### **2. Query Employees with High Stress**  
Using SQL, we filter employees who reported **"High" stress levels**.  
```python
from preswald import query

sql = "SELECT * FROM Impact_of_Remote_Work_on_Mental_Health_csv WHERE Stress_Level = 'High'"
filtered_df = query(sql, "Impact_of_Remote_Work_on_Mental_Health_csv")
```

### **3. Interactive UI for Analysis**  
We build a simple UI with **text headers, tables, and sliders** to allow interactive data exploration.  
```python
from preswald import table, text, slider

text("# Employee Well-being Analysis")  # Title
table(filtered_df, title="High Stress Employees")  # Show filtered employees

# Slider to filter employees by work hours
threshold = slider("Minimum Hours Worked Per Week", min_val=20, max_val=60, default=40)
table(df[df["Hours_Worked_Per_Week"] > threshold], title="Employees Working More Than Threshold Hours")
```

### **4. Scatter Plot: Work Hours vs. Age**  
A **scatter plot** is created to show how **hours worked per week** relate to **employee age** and **satisfaction levels**.  
```python
from preswald import plotly
import plotly.express as px

fig = px.scatter(
    df, 
    x="Hours_Worked_Per_Week", 
    y="Age", 
    color="Satisfaction_with_Remote_Work", 
    labels={
        "Hours_Worked_Per_Week": "Hours Worked Per Week", 
        "Age": "Employee Age"
    },
    title="Scatter Plot of Hours Worked vs Age"
)

plotly(fig)
```

---

## **Deploying the App**  

1. **Generate an API key** from [Preswald Cloud](https://app.preswald.com/).  
2. **Deploy using the command:**  
   ```bash
   preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
   ```
3. **Access your live app** through the provided link.  

---
