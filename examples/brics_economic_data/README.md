# BRICS Economic Analysis App

## 📌 Overview

This project is a **Preswald app** designed to analyze **economic trends** in **BRICS nations (Brazil, Russia, India, China, South Africa)** using an interactive dashboard. It allows users to perform **time-series analysis** and **country-wise economic comparisons** with **Plotly visualizations** (Available at: https://brics-economic-data-kqocrt68-ndjz2ws6la-ue.a.run.app).


---

## 📂 Dataset Source

The dataset used in this project contains **economic indicators** for BRICS nations over several years. It is sourced from:

- **[World Development Indicators (WDI) - The World Bank](https://databank.worldbank.org/source/world-development-indicators)**
- **Kaggle and Open Data Portals** for publicly available economic data


---

## 🚀 What This App Does

This **Preswald app** allows users to:

1. **Explore Economic Trends** – Visualize how key indicators (e.g., GDP, income, inflation) change over time.
2. **Compare BRICS Economies** – See economic differences between BRICS nations using **bar charts**.
3. **Interact with Data** – Users can **select specific years** and **adjust thresholds** dynamically.

---

## ⚙️ How to Run the App

### **1️⃣ Install Preswald**

Ensure you have Preswald installed. If not, install it using:

```sh
pip install preswald
```

### **2️⃣ Navigate to the Project Folder**
```sh
cd path/to/your/main/app/folder
```

### **3️⃣ Run the App Locally**

```sh
preswald run
```

💡 Make sure that hello.py is in the same folder as the preswald.toml file, since Preswald references it by default.

## 🌍 How to Deploy the App

### **1️⃣ Get an API Key**
1. Go to app.preswald.com.
2. Create a New Organization (top-left corner).
3. Navigate to Settings > API Keys.
4. Generate and copy your Preswald API key.

### **2️⃣ Deploy the App**

Run the deployment command:
```sh
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```

Replace:

```sh
<your-github-username> with your GitHub handle.
<structured-api-key> with your Preswald API Key.
```