# High Diamond Ranked 10min Data Analysis

This project contains a **Preswald** app (`hello.py`) that explores a League of Legends dataset—specifically, **high-diamond-ranked matches** truncated at the 10-minute mark. The app demonstrates various ways to **filter, visualize, and summarize** the data using Preswald components and Plotly.

---

## Dataset

- **Name**: `highdiamond.csv`  
- **Location**: `data/highdiamond.csv`
- **Description**: Each row represents a single League of Legends game at the 10-minute mark, including columns for Blue/Red kills, wards placed, total gold, and whether Blue side ultimately won.  
- **Source**: https://www.kaggle.com/datasets/bobbyscience/league-of-legends-diamond-ranked-games-10-min

### Key Columns

- `blueWardsPlaced`: Number of wards placed by the Blue team in the first 10 minutes.  
- `blueKills`: Number of kills the Blue team achieved in the first 10 minutes.  
- `blueTotalGold`: Total gold accumulated by the Blue team at 10 minutes.  
- `blueWins`: Indicates if the Blue team eventually won (`1` for win, `0` for loss).  
- Similarly for the Red team: `redWardsPlaced`, `redKills`, `redTotalGold`, etc.

---

## App Overview

1. **SQL Query Filter**  
   Shows rows where `blueWardsPlaced > 50` using Preswald’s `query()` and `table()`.

2. **Interactive Slider Filters**  
   Two sliders let the user filter games by:
   - Minimum Blue Kills  
   - Minimum Blue Wards Placed  

3. **Visualizations**:
   - **Histogram**: Distribution of `blueKills`.  
   - **Box Plot**: Comparison of `blueTotalGold` grouped by `blueWins`.  
   - **Correlation Heatmap**: Shows the relationship between numerical columns (like kills, wards, gold).  

4. **Aggregated Stats**  
   Displays average wards placed, kills, and gold by Blue side win/loss using SQL aggregation.

5. **Quick Summary Stats**  
   Presents the total number of games, total Blue side wins, and the Blue win rate.

---

# Running the Application Locally

## Prerequisites

Before getting started, ensure that the following requirements are met:

1. **Python Installation**: You need Python 3.7 or a later version installed on your system.

2. **Install Preswald**:
   Install the required dependencies along with Preswald by running the following command:
   
   ```bash
   pip install preswald
   ```

## Steps to Run the Application

1. **Obtain the Project Files**:
   - Clone the repository or download the necessary files.

2. **Prepare Your Dataset**:
   - Ensure the `data.csv` file is placed in the correct directory.
   - The dataset should be cleaned, and missing values should be filled using the median where applicable.

3. **Start the Application**:
   - With all dependencies installed and the dataset ready, launch the application by executing:
   
   ```bash
   preswald run
   ```
   - This will initiate a local instance of the app.
   - Open your browser and navigate to the displayed local URL (e.g., `http://127.0.0.1:8000`).

---

# Deploying the Application

## 1. **Deploying Locally via Preswald (Development Mode)**

Once the application runs successfully on your local machine, you can deploy it using **Preswald's** deployment features.

- Ensure you are logged into **Preswald** and have the necessary API credentials.
- Obtain an API key by visiting the [Preswald API Keys page](https://app.preswald.com/settings/api-keys).
- Deploy your application by running:
  
  ```bash
  preswald deploy --target structured --github --api-key YOUR_API_KEY
  ```
  Replace `YOUR_API_KEY` with your actual key.

## 2. **Deployment Instructions**

- **Create an Organization**: Sign up or log into **Preswald** at [Preswald's website](https://app.preswald.com/) and create a new organization.
- **Generate an API Key**: Visit **Settings > API Keys** to create a new key.
- **Deploy the App**: Use the `preswald deploy` command to push your application live.

Once deployed, a live preview link will be generated, allowing you to access and share the application easily.

## Additional Information

- **Data Configurations**: Modify `preswald.toml` to manage data connections.
- **Handling Sensitive Data**: Store credentials such as passwords and API keys in `secrets.toml`.
- **Running the App Locally**: Use `preswald run` for local execution.

Following these steps ensures a smooth setup and deployment of your application.