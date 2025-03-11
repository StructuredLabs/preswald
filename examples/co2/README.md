# PresWald CO2 Emissions Analysis App

## Dataset Source
This app utilizes the **CO2 Historical Overview Dataset**, which includes:
- **Real GDP (USD)**: Inflation-adjusted economic growth.
- **GDP Growth (%)**: Annual economic growth rate.
- **World Population**: Global population count.
- **CO2 Emissions (tons)**: Fossil fuel-related emissions data.
- **CO2 Emissions Per Capita**: Average emissions per person.

This dataset is ideal for economic, environmental, and sustainability research.

## What This App Does
This PresWald application allows users to explore **global CO2 emissions trends** alongside economic and population data. Key features include:
- **📊 Dynamic Data Filtering**: Set a CO2 emissions threshold to view relevant data.
- **📋 Interactive Data Table**: View key statistics filtered by emissions levels.
- **📈 Visualizations**:
  - **📉 Line Chart**: CO2 emissions trends over time.
  - **📊 Bar Chart**: Yearly CO2 emissions comparison.
  - **🔬 Scatter Plot**: Relationship between GDP and CO2 emissions.

## 🛠 How to Run Locally
### 1️⃣ Install PresWald
Ensure you have Python installed, then run:
```sh
pip install preswald
```

### 2️⃣ Initialize the Project
```sh
preswald init co2_analysis
cd co2_analysis
```

### 3️⃣ Place Your Dataset
Move the `co2.csv` dataset to the `data/` directory inside your project.

### 4️⃣ Run the Application
Modify `hello.py` with the provided app code and start the server:
```sh
preswald run
```
Your app should now be accessible locally.

## 🚀 Deployment Instructions
### 1️⃣ Get a PresWald API Key
- Go to [PresWald](https://app.preswald.com).
- Create an organization.
- Navigate to **Settings > API Keys**.
- Generate and copy the API key.

### 2️⃣ Deploy to Structured Cloud
Run the following command in your project directory:
```sh
preswald deploy --target structured --github --api-key <structured-api-key>
```
Replace `<structured-api-key>` with your actual API key.

### 3️⃣ Verify Deployment
Once deployed, a **live preview link** will be provided. Open it in your browser to confirm that the app is running as expected.
