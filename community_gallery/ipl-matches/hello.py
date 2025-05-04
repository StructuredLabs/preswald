from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

text("# IPL Analysis")

# Load the CSV
connect()
df = get_df('matches')

#---------------------------
# Matches Per Year
#---------------------------
text("## 1. Matches Played Per Year")
sql = """
    SELECT strftime('%Y', date) AS year, COUNT(*) AS season
    FROM matches
    GROUP BY year
    ORDER BY year
"""
yearly_matches = query(sql, "matches")

fig = px.line(
    x=yearly_matches["year"],
    y=yearly_matches["season"],
    labels={"x": "Year", "y": "Matches Played"},
)
fig.update_traces(line=dict(color="#74ae54"))
plotly(fig)

text(
    "### Insights from Matches Per Year:\n"
    f"- **{yearly_matches['year'].iloc[yearly_matches['season'].idxmax()]}** saw the highest number of matches played **{yearly_matches['season'].max()} games**, marking a peak in league activity.\n"
    "- The rise in matches indicates league expansion, new teams, and higher fan engagement globally.\n\n"
    "### Conclusion:\n"
    "The league’s evolution — from early growth to recent spikes — mirrors its global success, adapting to fan demand and competitive balance!"
)

#----------------------
# Most Successful Teams
#----------------------
text("## 2. Most Successful Teams")
sql = """
    SELECT winner, COUNT(winner) AS total_wins 
    FROM matches 
    WHERE winner IS NOT NULL 
    GROUP BY winner 
    ORDER BY total_wins DESC
"""
team_wins = query(sql, "matches")

threshold = slider("Number of Top Teams to Display", min_val=3, max_val=20, default=5)

fig = px.bar(team_wins.head(threshold), x="winner", y="total_wins", title=f"Top {threshold} Most Successful Teams", color_discrete_sequence=["#74ae54"])
plotly(fig)

top_team = team_wins.iloc[0]["winner"]
top_team_wins = team_wins.iloc[0]["total_wins"]
other_top_teams = team_wins.iloc[1:5]["winner"].tolist()
other_top_teams_list = ", ".join(other_top_teams)

text(
    "### Insights from Most Successful Teams:\n"
    f"- **{top_team} stands as the most successful team**, with an impressive **{top_team_wins} wins**, showcasing consistent dominance on the field.\n"
    f"- Other top-performing teams include **{other_top_teams_list}**, each with remarkable performances contributing to their legacy.\n\n"
    "### Conclusion:\n"
    "The dominance of top teams proves that success isn’t accidental — it’s built on strategy, resilience, and game-changing performances. Yet, the chase for the crown remains wide open, with every season inviting new challengers to rise."
)

#-----------------------------
# Toss Win Impact on Match Win
#-----------------------------
text("## 3. Toss Win Impact on Match Win")
toss_wins = (df["toss_winner"] == df["winner"]).sum()
total_matches = len(df)
toss_win_percentage = (toss_wins / total_matches) * 100

fig = px.pie(
    names=["Toss Winner Won", "Toss Winner Lost"],
    values=[toss_wins, total_matches - toss_wins],
    color_discrete_sequence=["#a1e16f", "#74ae54"],
)
plotly(fig)

text(
        "### Insights from Toss Impact:\n"
        f"- **Teams that win the toss** end up winning the match **{toss_win_percentage:.2f}%** of the time, suggesting a strategic edge.\n"
        "- Captains who make the right call after the toss — whether to bat or field — often turn that advantage into a win.\n\n"
        "### Conclusion:\n"
        "While toss wins don't guarantee victory, they set the stage for better decision-making, impacting match outcomes."
    )

#------------------------
# Toss Decision Breakdown
#------------------------
text("## 4. Toss Decision Breakdown")
sql = """
    SELECT toss_decision, COUNT(*) AS decision_count
    FROM matches
    GROUP BY toss_decision
    ORDER BY decision_count DESC
"""
toss_decision = query(sql, "matches")

fig = px.pie(
    toss_decision,
    names="toss_decision",
    values="decision_count",
    hole=0.4,
    color_discrete_sequence=["#a1e16f", "#74ae54"],
)
plotly(fig)

most_common_decision = toss_decision.iloc[0]["toss_decision"]

text(
    "### Insights from Toss Decisions:\n"
    f"- **The most common toss decision is to {most_common_decision} first**, reflecting a strategic preference among captains.\n"
    "- Teams opting to field often aim to chase down a known target, while batting first suits teams with strong bowling depth.\n\n"
    "### Conclusion:\n"
    "Toss decisions reflect the team's strengths — batting dominance or chasing confidence — influenced by pitch behavior and team balance."
)