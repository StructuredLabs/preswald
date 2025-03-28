from preswald import connect, text, slider, table, plotly
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


connect()

# Load the dataset
df = pd.read_csv("data/league_stats.csv")

text("# ⚽ European Football League Explorer")
text("Discover the top-performing teams across Europe's elite leagues!")

# Add a year range slider
min_year = df['season'].min().split('-')[0]
max_year = df['season'].max().split('-')[0]
start_year = slider("Year", 
                   min_val=min_year, 
                   max_val=max_year, 
                   default=min_year,
                   step=1)

# Filter data based on the selected year
df = df[df['season'].str.startswith(str(start_year))]

# Interactive filters
min_points = slider("Minimum Points", 
                   min_val=0, 
                   max_val=100, 
                   default=50,
                   step=1)  # Small step for smooth drag

min_goals = slider("Minimum Goals Scored", 
                  min_val=0, 
                  max_val=150, 
                  default=30,
                  step=1)

# Filter data
filtered_df = df[
    (df["points"] >= min_points) &
    (df["goals_for"] >= min_goals)
]

if not filtered_df.empty:
    # Add visual feedback for current filter values
    text(f"**Current Filters:**  \n"
            f"- Start Year: {start_year}  \n"
            f"- Minimum Points: {min_points}  \n"
            f"- Minimum Goals: {min_goals}")
    
    text("## 📊 League Comparison")
    fig = px.scatter(filtered_df, 
                        x="goals_for", 
                        y="points", 
                        color="competition",
                        size="wins", 
                        hover_name="squad", 
                        labels={"goals_for": "Goals Scored", "points": "Points"},
                        title="Goals vs Points Across Leagues")
    plotly(fig)
    
    text("## 🥅 Goal Difference Analysis")
    filtered_df['goal_difference'] = filtered_df['goals_for'] - filtered_df['goals_against']
    fig2 = px.bar(filtered_df, 
                    x="squad", 
                    y="goal_difference", 
                    color="competition",
                    hover_data=["goals_for", "goals_against"],
                    labels={"goal_difference": "Goal Difference"},
                    title="Team Goal Differences")
    fig2.update_xaxes(tickangle=45)
    plotly(fig2)
    
    text("## 🌟 Top Scorers")
    top_scorers = filtered_df.nlargest(5, "goals_for")
    fig3 = go.Figure(data=[go.Bar(x=top_scorers["squad"], 
                                    y=top_scorers["goals_for"],
                                    text=top_scorers["goals_for"],
                                    textposition='auto')])
    fig3.update_layout(title="Top 5 Scoring Teams")
    plotly(fig3)
    
    text("## 🏆 Top Performers")
    table(filtered_df[["competition", "squad", "points", "wins", "goals_for", "goals_against"]])

else:
    text("No teams match the selected criteria. Try adjusting the sliders!")


