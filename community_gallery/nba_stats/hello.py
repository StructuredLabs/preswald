from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import numpy as np
import plotly.express as px

# Load the CSV
connect() # load in all sources 
df = get_df('2023_nba_player_stats_csv')

# if df is None:
#     text("Data not loaded")
# else:
    # text(f"Loaded {len(df)}")

# UI 

# Convert int64 to int for json error
for col in df.select_dtypes(include=[np.int64]).columns:
    df[col] = df[col].astype(int)

text("# 2023 NBA Stats Comparison App")

# slider for points 
threshold = slider("Points Threshold", min_val=0, max_val=int(df["PTS"].max()), default = 50)

df_threshold = df[df["PTS"] > threshold]

table(df_threshold, title=f"NBA Players Scoring More Than {threshold} Points in 2023")

# fg vs points scatter
fig = px.scatter(df_threshold, x = "PTS", y = "FG%", color = "Team",
                    hover_data = ["PName", "Age", "AST", "REB", "STL"],
                    title = "Field Goal % vs. Points Scored",
                    labels = {"PTS": "Total Points", "FG%": "Field Goal Percentage"})

fig.update_traces(textposition = "top center", marker = dict(size=12, color="blue"))
fig.update_layout(template = "plotly_white")

plotly(fig) 


table(df, title="Full NBA Player Stats Dataset")

