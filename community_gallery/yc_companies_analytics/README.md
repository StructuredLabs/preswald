
# YC Companies Analysis (2000-2025)

## Overview
This interactive dashboard provides insights into Y Combinator (YC) companies from 2000 to 2025. The analysis explores company distribution, team sizes, industries, statuses, and locations. The application is built with **Preswald**, enabling rapid development of an interactive, data-driven web application.

**Live Dashboard:** [YC Companies Analytics](https://yc-companies-analytics-988067-ly9kyzm7-ndjz2ws6la-ue.a.run.app)

---

## Dataset
This project uses a manually scraped dataset from the **YC Directory**, containing detailed information about YC companies, including:
- **Company details** (name, slug, website)
- **Batch information** (batch name, year)
- **Team size** (number of employees)
- **Status** (Active, Inactive, etc.)
- **Industries** (e.g., B2B, Fintech, AI)
- **Locations** (e.g., San Francisco, New York)

**Source**: The data was manually scraped from the YC Directory.

---

## Features

### Interactive Filters
- **Batch Selection**: Filter companies by specific batches (e.g., W23, S24).
- **Team Size Range**: Adjust the team size range to filter companies.
- **Status Filter**: Filter by company status (e.g., Active, Inactive).

### Analysis Views

#### 1. **Company Distribution by Batch**
- Bar chart showing the number of companies per batch.
- Insights into batch growth over time.

#### 2. **Team Size Distribution**
- Histogram showing the distribution of team sizes.
- Mean and median team size calculations.

#### 3. **Industry Breakdown**
- Pie chart showing the proportion of companies in each industry.
- Top 10 industries by company count.

#### 4. **Company Status Analysis**
- Pie chart showing the distribution of company statuses.
- Percentage of active vs. inactive companies.

#### 5. **Location Analysis**
- Bar chart showing the top 10 locations by company count.
- Geographic distribution of companies.

---

## Data Visualization
- **Interactive Plotly Charts**: Bar charts, pie charts, histograms.
- **Real-Time Updates**: Visualizations update dynamically based on filters.
- **Responsive Design**: Works seamlessly across devices.

---

## How to Run

### 1. Set Up Your Environment
```bash
# Install Preswald and required libraries
pip install preswald pandas plotly

# Create a new project directory
preswald init yc_companies_analytics
cd yc_companies_analytics
```

### 2. Configure Data Source
Create a `preswald.toml` file in your project directory with the following content:
```toml
[data.yc_companies]
path = "./data/yc_companies.csv"
```

### 3. Add Your Dataset
Place your `yc_companies.csv` file in the `data/` folder.

### 4. Run the App Locally
```bash
preswald run 
```
This will start a local development server. Access the dashboard at the URL shown in the terminal.

---

## Deployment
Deploy to Structured Cloud:
```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```
Replace `<your-github-username>` and `<structured-api-key>` with your credentials.

---

## Implementation Details

### Key Components
- **Data Processing**:
  - Cleaned and transformed raw data (e.g., split industries and locations).
  - Calculated key metrics (e.g., average team size, industry percentages).
- **UI Components**:
  - Interactive sliders and filters.
  - Real-time updates for visualizations.
  - Responsive table for detailed data exploration.

### Analysis Features
- **Batch Analysis**: Growth trends over time.
- **Team Size Analysis**: Distribution and typical team sizes.
- **Industry Analysis**: Most common industries and their proportions.
- **Status Analysis**: Active vs. inactive companies.
- **Location Analysis**: Geographic distribution of companies.

---

## Libraries Used
- **Preswald**: Core framework for the application.
- **Pandas**: Data manipulation and analysis.
- **Plotly**: Interactive data visualizations.
- **NumPy**: Numerical operations.
---
## About This Project
This project was created to demonstrate the power of **Preswald** for building interactive data applications. It provides valuable insights into Y Combinator companies and serves as an example for the **Preswald Community Gallery**. This dashboard was created as part of the Structured Labs Coding Assessment.
```


