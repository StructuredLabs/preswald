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

- **Step 1:** Select one or more **country groups** using checkboxes.
- **Step 2:** Choose a country from the dropdown.
- **Step 3:** View an interactive scatter plot showing the relationship between developer experience and annual salary.
- **Step 4:** Explore the top 20 responses in a structured table.

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

## ❗ Troubleshooting

If you see an error like:
```
Error: Unable to load dataset. Please ensure the data file is in the 'data/' directory.
```
✅ **Solution:** Follow the dataset download instructions above and place the dataset files inside `data/` before running the app.
