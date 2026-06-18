# Preswald App for Olympics Data Visualization

## 🎯 Overview

I have created a Preswald App for Olympics Data Visualization.

🌐 Live Demo: [Olympics Data Visualization](https://rahul-preswald-veh8rams-ndjz2ws6la-ue.a.run.app/)

### 📊 Dataset Used

The dataset used is from Kaggle: [Kaggle Dataset](https://www.kaggle.com/datasets/amanrajput16/olympics-medal-list-1896-2024?resource=download)

It contains country-wise information from 1896 to 2024, detailing each country's rank, gold, silver, and total medals.

#### Dataset Structure (Sample Rows):

```
Year,Rank,NOC,Gold,Silver,Bronze,Total
2024,1,United States,40,44,42,126
2024,2,China,40,27,24,91
2024,3,Japan,20,12,13,45
2024,4,Australia,18,19,16,53
2024,5,France,16,26,22,64
```

*Note: The dataset contains multiple rows; this is just a sample.*

### 🚀 Features of the App

- View USA's performance from 1896 to 2024.
- See the top-ranked country in each Olympic Games.
- Use an interactive slider to filter countries by the number of gold medals (showing countries with at least that many gold medals).
- Visualize data through plots:
  - Country vs Gold Medals
  - Country vs Total Medals
- Display the complete dataset in a table format.

---

## 🧑🏻‍💻 How to Run the App Locally

### Prerequisites

#### Install Python:

Ensure you have Python 3.7 or higher installed. You can download Python from [here](https://www.python.org/downloads/).

#### Install Required Packages:

The project relies on the following Python libraries:

- `pandas` for data manipulation
- `plotly` for visualizations
- `preswald` for app functionality
- Other dependencies as required for your environment

To install the required packages, run the following command in your terminal:

```sh
pip install pandas plotly preswald
```

### Running the App

1. Clone the repository or download the files.
2. **Prepare the Dataset:** Ensure `data.csv` is in the correct directory.
3. **Run the App:** Once all dependencies are installed and your dataset is in place, execute the following command in your terminal:
   ```sh
   preswald run
   ```
   This will start the app locally, and you can access it in your web browser at the provided local URL (e.g., `http://127.0.0.1:8501`).

---

## ☁️ How to Deploy the App

### Deploy Your App to Structured Cloud**

Once your app is running locally, deploy it.

1. **Get an API key**
    
    - Go to [app.preswald.com](https://app.preswald.com/)
    - Create a New Organization (top left corner)
    - Navigate to **Settings > API Keys**
    - Generate and copy your **Preswald API key**
      
2. **Deploy your app using the following command:**
    ```
    preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
    ```
    Replace `<your-github-username>` and `<structured-api-key>` with your credentials.
    
3. **Verify the deployment**
    
    - Once deployment is complete, a **live preview link** will be provided.
    - Open the link in your browser and verify that your app is running.
---

Enjoy exploring the Olympics data through this interactive and visual dashboard!

