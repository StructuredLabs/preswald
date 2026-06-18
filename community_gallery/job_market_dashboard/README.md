## **AI-Powered Job Market Insights Dashboard**

Welcome to the **AI-Powered Job Market Insights Dashboard**! This interactive data dashboard lets you explore current AI job market trends, including in-demand **job titles**, **salary distribution**, and **skills required**. The app uses real-world data from the **AI-powered job market dataset** to give you valuable insights into what's trending in the job market right now.

You can access the dataset used in this project from [Kaggle's AI-Powered Job Market Insights Dataset](https://www.kaggle.com/datasets/uom190346a/ai-powered-job-market-insights).

### **📝 Overview**
The dataset used in this project provides a comprehensive overview of AI job market data, covering job titles, salary figures, required skills, and job trends.

With this dashboard, you can:
- **Explore the most in-demand job titles** within the AI field.
- **Filter job listings** based on **salary ranges** and **skills**.
- Visualize **salary distributions** and track **job market trends** over time.

---

### **📦 Requirements**
To get the dashboard up and running on your local machine, you'll need a few things installed first. Here's what you need:

- **Python 3.6+** (make sure you have an appropriate version of Python installed)
- **Preswald** (for building the interactive dashboard)
- **Pandas** (for handling and manipulating data)
- **Plotly** (for creating data visualizations)

You can install all the required dependencies in one go by running:

```sh
pip install -r requirements.txt
```

---

### **📁 File Structure**
Here's an overview of the file structure of this project, so you know where to find everything:

```
job_market_dashboard/
│── community_gallery/
│   ├── job_market_dashboard/
│   │   ├── hello.py               # Main script for the app              
│   │   ├── data/
│   │   │   ├── job_market_data.csv # Dataset containing AI job market data
│   │   ├── images/
│   │   │   ├── favicon.ico        # Favicon for the dashboard
│   │   │   ├── logo.png           # Logo for the dashboard
│   │   ├── README.md              # This documentation
│   │   ├── preswald.toml          # Preswald configuration file
│   │   ├── pyproject.toml         # Python project configuration
│   │   ├── secrets.toml           # Secrets configuration (for storing API keys)
```

---

### **📊 Key Features**
This dashboard provides several useful features to analyze and interact with the job market data:

#### **1. Job Market Insights**
- View the **top 10 in-demand job titles** based on the dataset.
- For each job title, you'll see how many job postings are available in that category.

#### **2. Filtering by Salary and Skills**
- **Filter job listings** by setting a **minimum** and **maximum salary**.
- You can also search for jobs requiring specific **skills** using a text input.

#### **3. Data Visualizations**
The dashboard offers two main visualizations:
- **Salary Distribution**: A **histogram** that shows the salary distribution across job titles.
- **Job Trends**: A **line graph** that visualizes how the number of job postings has changed over time.

---

### **⚙️ Installation and Setup**

Follow these steps to run the app locally:

1. **Clone the repository**:
   First, you'll need to clone the repository to your local machine:
   ```sh
   git clone https://github.com/genesis0x/job-market-dashboard.git
   cd job-market-dashboard
   ```

2. **Install the required dependencies**:
   Next, install all the necessary Python packages by running:
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure the Dataset**:
   - Make sure you place the `job_market_data.csv` dataset file inside the `data/` folder.
   - Check that the file is properly loaded in the **Preswald** configuration (the `preswald.toml` file).

4. **Run the App Locally**:
   Once everything is set up, you can start the dashboard locally by running:
   ```sh
   preswald run
   ```
   This will launch the app, and you can view it in your browser at [http://localhost:8501](http://localhost:8501).

---

### **🔄 Deploying the App**

To deploy the app on **Preswald Structured Cloud**, follow these steps:

1. **Get your API Key**:
   - Sign up at [Preswald](https://app.preswald.com), create an organization, and go to **Settings > API Keys** to get your API key.

2. **Deploy the app**:
   Now you're ready to deploy the app to Preswald's cloud! Use the following command:
   ```sh
   preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
   ```
   This will deploy your app, and it should be accessible via the Preswald platform.