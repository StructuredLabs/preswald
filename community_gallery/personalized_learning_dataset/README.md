# 📊 Personalized Learning & Performance Dashboard

### *Insights into student performance, behavior, and learning preferences.*

## 📂 Dataset Source
- **Dataset:** [Personalized Learning and Adaptive Education Dataset](https://www.kaggle.com/datasets/adilshamim8/personalized-learning-and-adaptive-education-dataset)
- **Description:** This dataset provides insights into student engagement, learning styles, and performance metrics.
- **Key Features:**
  - Student demographics (Age, Gender, Education Level)
  - Learning style preferences (Visual, Auditory, Kinesthetic, etc.)
  - Course performance metrics (Quiz Scores, Time Spent on Videos)
  - Engagement and assessment statistics

---

## 🚀 About This App
This **Preswald-powered dashboard** allows educators and analysts to explore student performance and engagement. 

### 🔥 **Key Features:**
- 🎯 **Learning Insights Summary** – Displays Key Performance Indicators such as:
  - **Average Quiz Scores**
  - **Time Spent on Videos**
  - **Top Performing Courses**
  - **Pass Rate (≥70%)**
- 🔗 **Time Investment vs. Performance** – Shows how video engagement correlates with quiz scores.
- 🔎 **Interactive Student Explorer** – Filter students by quiz score thresholds to identify top performers.

---

## 🚀 How to Run

### **1. Set Up Your Environment**  
Install **Preswald** and dependencies:  
`pip install preswald`  

Create a new project directory:  
`preswald init learning_dashboard`  
`cd learning_dashboard`  

### **2. Configure Data Source**  
Create a `preswald.toml` file in your project directory with the following content:  
`[data.personalized_learning_dataset]`  
`path = "./data/personalized_learning_dataset.csv"`  

### **3. Download the Dataset**  
Download the dataset from Kaggle and place it in the `data/` folder:  
`mkdir data`  
`mv path/to/downloaded_dataset.csv data/personalized_learning_dataset.csv`  

### **4. Run the App Locally**  
`preswald run hello.py`  

This will start a local development server, and you can access the dashboard at the URL shown in the terminal.

---
## 🚀 Deploying Your App

### 1️⃣ Once your app is running locally, deploy it.

### 2️⃣ Get an API Key
- Go to **[app.preswald.com](https://app.preswald.com)**
- **Create a New Organization** (top left corner)
- Navigate to **Settings > API Keys**
- **Generate and copy** your Preswald API key

### 3️⃣ Deploy Your App
Run the following command, replacing `<your-github-username>` and `<structured-api-key>` with your actual credentials:
