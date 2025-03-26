# The dataset source.

The dataset comes from Kaggle and contains historical information about FIFA World Cup matches. This dataset includes details such as:

    - Year of the match
    - Stadium and City where the match took place
    - Attendance (number of spectators)
    - Various other match-specific attributes

# What your app does.

Your Preswald app is an interactive data visualization and exploration tool that allows users to:

    1. View World Cup Match Data: Display a table of matches with information about the year, stadium, city, and attendance.
    2. Filter Data Dynamically: Use a slider to filter and display matches with an attendance greater than a user-defined threshold.
    3. Visualize Attendance Trends: Display an interactive scatter plot using Plotly to visualize the relationship between stadiums, cities, and attendance.
    User Interface: Personalized greeting and a clean, responsive interface powered by Preswald.

# How to run and deploy it.

1. Set Up the Environment

python -m venv venv
## Linux/macOS
source venv/bin/activate
## Windows
venv\Scripts\activate

2. Install Dependencies

pip install preswald

3. Install the DataSet

https://www.kaggle.com/datasets/abecklas/fifa-world-cup

4. Run the App

preswald run community_gallery/world_cup_matches

