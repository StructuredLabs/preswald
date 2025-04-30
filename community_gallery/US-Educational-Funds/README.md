#Preswald Project

# U.S. Educational Finances Analysis

## Dataset

This project uses the **[U.S. Educational Finances Dataset](https://www.kaggle.com/datasets/noriuk/us-educational-finances)** , which contains data on school district expenditures, revenues, enrollments, and student performance metrics across U.S. states.

## About The App

This interactive app, built with **Preswald**, analyzes the relationship between **education funding, expenditures, and student performance** at both the **state and district levels**. 

### **Key Features**
✔️ **Data Merging & Cleaning**: Combines multiple datasets (`districts`, `states`, `naep`) for analysis.  
✔️ **Per-Student Spending Analysis**: Calculates **expenditure and revenue per student** at state and district levels.  
✔️ **Trend Visualization**: Graphs **revenue vs. expenditure trends** across states.  
✔️ **Performance vs. Spending Analysis**: Examines how **per-student expenditure impacts test scores**.  

---

## Installation & Setup

### **Install Dependencies**
Before running the app, install the required packages:
```
pip install preswald
```

- `git clone https://github.com/StructuredLabs/preswald.git`
- `cd preswald/community_gallery/US-Educational-Funds`
- `preswald run`

## **Note: Large Dataset & Memory Issue**
Due to the large size of `districts.csv`, **the server may run out of memory while rendering visualizations**.  
**To prevent crashes, please reduce the dataset size before running the app.**

## Deployment in Render 
1. Go to https://render.com/
2. Sign in with GitHub and connect your repository.
3. Click "New Web Service".
4. Select "GitHub" and choose your repository.
5. Configure Deployment Settings
6. Create a .txt file for the Build Command
7. Start the app