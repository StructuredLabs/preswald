"""
File: hello.py
Project: my_example_project
Description: This script initializes and starts the Preswald server, establishes a database connection,
             loads and validates the dataset, and provides data filtering and visualization for the
             Premier Lacrosse League 2019-2022 analysis.

Author: Dom Scordino
Created: 3/13/2025
Last Modified: 3/14/2025
"""

import uvicorn
import plotly.express as px
from preswald import connect, get_df, query, table, text, slider, plotly
from preswald.main import start_server

# Disable Uvicorn logging issues
def patched_configure_logging(*args, **kwargs):
    pass

uvicorn.Config.configure_logging = patched_configure_logging

# Ensure Preswald starts ONLY ONCE
if __name__ == "__main__":
    start_server()

# Establish Database Connection
print("Connecting to data sources...")
try:
    connect()
    print("Successfully connected to data sources.")
except Exception as e:
    print(f"Error connecting to data sources: {e}")

# Load Dataset
print("Attempting to load dataset...")
df = get_df("sample_csv")

if df is None:
    print("Error: Dataset not found. Check data source configuration.")
    text("Error: Dataset not found. Please check your data source configuration.")
    exit()

print("Dataset loaded successfully:")
print(df.head())

# Validate Required Columns
REQUIRED_COLUMNS = {"scores_for", "scores_against", "win_percentage", "faceoff_percentage", "finishing_position", "shooting_efficiency", "Team"}

if not REQUIRED_COLUMNS.issubset(df.columns):
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    print(f"Error: Dataset missing required columns: {missing_columns}")
    text(f"Error: Dataset is missing required columns: {missing_columns}")
    exit()

# Query Full Dataset
sql = "SELECT * FROM sample_csv"
raw_df = query(sql, "sample_csv")

# UI Header
text("# Premier Lacrosse League 2019-2022 Analysis")

# Filtering Controls
shot_efficiency_threshold = slider("Shooting Efficiency Threshold", min_val=30, max_val=40, default=30)
win_threshold = slider("Win % Threshold", min_val=0, max_val=100, default=0)
finishing_position_threshold = slider("Max Finishing Position", min_val=1, max_val=8, default=8)

# Data Filtering
df_filtered = df[
    (df["shooting_efficiency"] > shot_efficiency_threshold) &
    (df["win_percentage"] > win_threshold) &
    (df["finishing_position"] <= finishing_position_threshold)
]

# Scatter Plot: Win % vs Shooting Efficiency
if not df_filtered.empty:
    def get_team_status(row):
        """Assigns a status category based on finishing position."""
        if row["finishing_position"] == 1:
            return "Won Final"
        elif row["finishing_position"] <= 4:
            return "Made Semifinals"
        return "Out of Playoffs"

    df_filtered["Status"] = df_filtered.apply(get_team_status, axis=1)

    fig = px.scatter(
        df_filtered,
        x="win_percentage",
        y="shooting_efficiency",
        text="shooting_efficiency",
        title="Win % vs. Shooting Efficiency",
        hover_data=["Season", "Team", "finishing_position"],
        color=df_filtered["Status"]
    )

    # Improve Readability of the Plot
    fig.update_traces(textposition="top center", marker=dict(size=12))
    fig.update_layout(template="plotly_white")

    # Display Plot
    plotly(fig)

# Filtered Data Table
table(
    df_filtered,
    title=f"Filtered Data (Max Position ≤ {finishing_position_threshold})"
)

print("Data filtering and visualization completed.")
