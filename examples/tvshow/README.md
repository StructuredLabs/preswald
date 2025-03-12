# TV Show and Movie Explorer

Find the app here- [TV Show and Movie Explorer](https://my-project-813590-ctee5ydx-ndjz2ws6la-ue.a.run.app/)

## Dataset Source

The dataset used in this project is derived from **Netflix Data Visualization**. The data includes **type**, **title**, **director**, **country**, **release_year**. This dataset allows for analysis and visualization of TV Shows and Movies.

The dataset used is a CSV file named `netflix_titles.csv`, which includes the following columns:
- **Type**: Type of Show
- **Title**: Name of the Show or Movie
- **Director**: Name of the director
- **Country**: Movie's country origin
- **Release Year**: Movie or Show release year etc.
## What Does the App Do?

The **TV Show and Movie Explorer** is an interactive dashboard that allows users to explore and visualize tv shows and movies from Netflix. It enables the following functionalities:

- **Show or Movie-Based Filtering**: Users can select a show or movie from a dropdown list to see options.
- **Release Year Filter**: The app allows users to filter shows or movies based on release year using a slider.
- **Display Table**: Displays the selected shows or movie data including their type, title, director, country, release_year, and rating.
- **Movie Locations on Map**: Displays the geographical locations of the shows or movies.

## How to Run the App Locally

### Prerequisites

1. **Install Python**: Ensure you have Python 3.10 or higher installed. You can download Python from [here](https://www.python.org/downloads/).
   
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

1. **Clone the repository**.
   
2. **Prepare the Dataset**: Make sure the `netflix_titles.csv` file is in the correct directory.

3. **Run the App**:
   Once all dependencies are installed and your dataset is in place, you can run the app locally by using the following command in your terminal:
   ```bash
   preswald run
   ```

   This will start the app locally, and you can open it in your web browser.

## How to Deploy the App

### 1. **Deploy Locally with Preswald** (for Development)

   Once you have the app working locally, you can deploy it using **Preswald**'s deployment tools.

   - Make sure you're logged in to Preswald and have the necessary API keys.
   
   - Run the following command to deploy the app to **Preswald**:
     ```bash
     preswald deploy --target structured --github --api-key YOUR_API_KEY hello.py
     ```

   Replace `YOUR_API_KEY` with your actual Preswald API key.

### 2. **Deployment Steps**:

   - **Create a New Organization**: Go to [Preswald's website](https://app.preswald.com/) and create a new organization.
   - **Generate an API Key**: Navigate to **Settings > API Keys** to generate a new API key.
   - **Deploy**: Use the `preswald deploy --target structured --github --api-key YOUR_API_KEY hello.py` command to deploy your app.

   After deployment, a live preview link will be generated. You can share the link or use it to access the app from any device.

## Additional Notes

- Ensure that the dataset is correctly formatted and updated for deployment.
---

Enjoy exploring TV shows and Movies from Netflix through this interactive and visual dashboard!
