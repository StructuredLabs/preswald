# Stack Overflow Developer Trends Explorer

## 📌 Overview

This application allows users to explore insights from the **Stack Overflow Developer Survey 2024** dataset. Users can filter by country and analyze developer compensation vs experience using an interactive visualization.

## 📊 Dataset Source

- **Source:** [Stack Overflow Developer Survey 2024 on Kaggle](https://www.kaggle.com/datasets/berkayalan/stack-overflow-annual-developer-survey-2024)
- **Download Instructions:**
  1. Visit the dataset page on Kaggle:
     👉 [Download Here](https://www.kaggle.com/datasets/berkayalan/stack-overflow-annual-developer-survey-2024)
  2. Click the Download button.
  3. Select **Download dataset as zip**
  4. Extract the files and place them in the `data/` directory inside this project.

## 🚀 Running the App

1. **Ensure you have Python 3.8+ installed**
   You can check by running:
   ```bash
   python --version
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\\Scripts\\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   preswald run
   ```

## 📖 How the App Works

1. **Filter Countries**: Select one or more country groups using checkboxes to narrow down the available countries.
2. **Choose a Dashboard View**: Navigate between **Experience vs. Compensation** and **Compare Countries** dashboards.
3. **Select Countries**:
   - In **Experience vs. Compensation**, choose a single country to analyze.
   - In **Compare Countries**, select up to three countries to compare.
4. **Apply Experience Filters**: Adjust minimum and maximum experience level using sliders to refine the dataset.
5. **Explore Visualizations**: View interactive scatter plots, bar charts, and histograms to analyze salary trends.
6. **Examine Raw Data**: The top 20 responses are displayed in a structured table.

## 🚀 Features

### 📊 Experience vs. Compensation
- **Scatter plot visualization** with trendline details (slope & R² value).
- **Salary distribution histogram** to analyze compensation trends.
- filter by:
  - Country
  - Experience level range using a slider.

### 🌍 Compare Countries
- Select up to three countries to compare salary and experience trends.
- **Box plot visualization** of salary distribution across selected countries.
- **Bar chart comparison** of median salaries per country.
- Filter by:
  - Experience level range using a slider.

### ✅ Additional Features
- **Dynamic filtering** of available countries based on selected country groups.
- **Clear instructions and user-friendly navigation**.
- **Responsive UI** with interactive visualizations.

### 📌 **Updated Deployment Instructions for README.md**
Here’s how we should structure the deployment section to closely match the official coding assessment guide while making it specific to your project:

## 🚀 Deploying Stack Overflow Developer Trends 2024 app to Structured Cloud

Once you verified that it runs locally, you can deploy it to Structured Cloud.

### 1️⃣ **Get an API Key**
1. Go to [app.preswald.com](https://app.preswald.com/).
2. Create a **New Organization** (top left corner).
3. Navigate to **Settings > API Keys**.
4. Generate and copy your **Preswald API key**.

### 2️⃣ **Deploy Your App**
Run the following command, replacing `<your-github-username>` and `<structured-api-key>` with your actual credentials:

```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```

### 3️⃣ **Verify the Deployment**
- Once deployment is complete, a **live preview link** will be provided.
- Open the link in your browser to verify that your app is running.

### 🔄 **Updating Your Deployment**
If you make changes to your app, redeploy using the same command:
```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```

## ⚠️ UI Design Decision: Checkbox Filtering for Country Selection

Preswald's `selectbox` component does not currently support scrolling or searching within long lists. To enhance usability, checkboxes are used to pre-filter the country selection dropdowns. This allows users to:
- Narrow down the list of available countries.
- Avoid excessive scrolling through long lists.
- Improve the user experience when selecting countries for analysis.

If Preswald introduces scrollable or searchable selectboxes in the future, this approach can be revisited.

## ❗ Troubleshooting

### Issue: Dataset Not Found
If you see an error like:
```
Error: Unable to load dataset. Please ensure the data file is in the 'data/' directory.
```
✅ **Solution:** Follow the dataset download instructions above and place the dataset files inside `data/` before running the app.

### Issue: Country Select Boxes Not Updating Immediately
In the **Compare Countries** section, when modifying the selected checkboxes for filtering countries, the **country dropdowns may not refresh immediately**. This appears to be a limitation in the current implementation of Preswald UI components.

✅ **Workaround:** If the country dropdowns do not update after modifying checkboxes, try switching to a different dashboard tab (e.g., "Experience vs. Compensation") and then switching back.

We will update the implementation if a better solution becomes available.