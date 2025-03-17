# ⚽ Club-Based Player Explorer

Find the app here- [FIFA23 Analayzer](https://preswald-fifa23-player-analysis-ucbcrhf2-ndjz2ws6la-ue.a.run.app/)

## Dataset Source

The dataset used in this project is derived from **FIFA 23 player data**. The data includes various attributes of football players, including their **overall rating**, **club name**, **nationality**, **player positions**, **physical stats**, and **performance attributes**. This dataset allows for analysis and visualization of player statistics and comparison between players from different clubs and countries.

The dataset used is a CSV file named `data.csv`, which includes the following columns:
- **Known As**: Player's known name
- **Full Name**: Full name of the player
- **Overall**: Overall rating of the player
- **Potential**: The player's potential rating
- **Club Name**: The club the player is associated with
- **Nationality**: The player's country of origin
- **Positions Played**: Positions the player plays (e.g., Forward, Midfielder)
- **Pace Total**, **Shooting Total**, **Dribbling Total**, **Passing Total**, **Defending Total**, **Physicality Total**: Stats related to the player's skills
- **Best Position**: The player’s best position on the field

The dataset is crucial for exploring different clubs and understanding player statistics on various metrics, such as physical strength, shooting ability, and overall ratings.

## What Does the App Do?

The **Club-Based Player Explorer** is an interactive dashboard that allows users to explore and visualize player data from FIFA 23. It enables the following functionalities:

- **Club-Based Filtering**: Users can select a football club from a dropdown list to see a filtered list of players who belong to that club.
- **Overall Rating Filter**: The app allows users to filter players by their overall rating using a slider.
- **Player Table**: Displays the selected players' data including their name, nationality, and overall rating.
- **Player Locations on Map**: Displays the geographical locations of the players on a world map, with point sizes representing the player's overall rating and point colors representing the player's role (e.g., Forward, Midfielder, Defender).
- **Player Strengths Radar Plot**: A radar plot is generated to display the top 5 players from the selected club, visualizing their strengths in different areas such as pace, shooting, dribbling, passing, defending, and physicality.

The app helps users better understand football players' performance across different clubs, compare strengths, and gain insights into player statistics in an interactive and visually appealing way.

## How to Run the App Locally

### Prerequisites

1. **Install Python**: Ensure you have Python 3.7 or higher installed. You can download Python from [here](https://www.python.org/downloads/).
   
2. **Install Required Packages**: The project relies on the following Python libraries:
   - `pandas` for data manipulation
   - `plotly` for visualizations
   - `preswald` for app functionality
   - Other dependencies as required for your environment

   To install the required packages, run the following command in your terminal:
   ```bash
   pip install pandas plotly preswald
   ```

### Running the App

1. **Clone the repository** or download the files.
   
2. **Prepare the Dataset**: Make sure the `data.csv` file is in the correct directory. The data should be properly cleaned, with any missing values filled by the median where appropriate.

3. **Run the App**:
   Once all dependencies are installed and your dataset is in place, you can run the app locally by using the following command in your terminal:
   ```bash
   preswald run
   ```

   This will start the app locally, and you can open it in your web browser at the provided local URL (e.g., `http://127.0.0.1:8000`).

## How to Deploy the App

### 1. **Deploy Locally with Preswald** (for Development)

   Once you have the app working locally, you can deploy it using **Preswald**'s deployment tools.

   - Make sure you're logged in to Preswald and have the necessary API keys. You can generate an API key by visiting [Preswald's API Keys page](https://app.preswald.com/settings/api-keys).
   
   - Run the following command to deploy the app to **Preswald**:
     ```bash
     preswald deploy --target structured --github --api-key YOUR_API_KEY
     ```

   Replace `YOUR_API_KEY` with your actual Preswald API key.

### 2. **Deployment Steps**:

   - **Create a New Organization**: Go to [Preswald's website](https://app.preswald.com/) and create a new organization.
   - **Generate an API Key**: Navigate to **Settings > API Keys** to generate a new API key.
   - **Deploy**: Use the `preswald deploy` command to deploy your app.

   After deployment, a live preview link will be generated. You can share the link or use it to access the app from any device.

## Additional Notes

- Ensure that the dataset is correctly formatted and updated for deployment.
- For further customization, you can modify the user interface, enhance the radar plot with more statistics, or adjust the map to handle more countries.
- You can also add more filters for advanced exploration (e.g., age, player position, etc.).

---

Enjoy exploring FIFA 23 players through this interactive and visual dashboard!
