from preswald import connect, get_df, plotly, text
import plotly.express as px

# Report Title
text("# UFC Records Dashboard")
text("This dashboard provides a visual breakdown of UFC records, including wins, finishes, striking accuracy, and grappling performance.")

# Load the CSV
connect()
df = get_df("sample_csv")

# 1. **Top Fighters by Wins** - Bar Chart
text("## Top Fighters by Wins")
wins_df = df[df["Type of Record"] == "Wins"]
fig1 = px.bar(wins_df, x="Name", y="Total", color="Name", title="Top Fighters by Wins")
plotly(fig1)

# 2. **Most Finishes in UFC History** - Bar Chart
text("## Most Finishes in UFC History")
finishes_df = df[df["Type of Record"] == "Finishes"]
fig2 = px.bar(finishes_df, x="Name", y="Total", color="Name", title="Most Finishes in UFC History")
plotly(fig2)

# 3. **KO/TKO vs Submission Wins** - Pie Chart
text("## KO/TKO Wins vs Submission Wins")
ko_sub_df = df[df["Type of Record"].isin(["KO/TKO Wins", "Submission Wins"])]
fig3 = px.pie(ko_sub_df, names="Type of Record", values="Total", title="KO/TKO vs Submission Wins")
plotly(fig3)

# 6. **Takedown Accuracy vs. Defense** - Scatter Plot
text("## Takedown Accuracy vs Defense")
takedown_df = df[df["Type of Record"].isin(["Takedown Accuracy", "Takedown Defense"])]
fig6 = px.scatter(takedown_df, x="Total", y="Rank", color="Name", title="Takedown Accuracy vs Defense", hover_data=["Type of Record"])
plotly(fig6)

# 7. **Knockdowns Landed Distribution** - Histogram
text("## Distribution of Knockdowns Landed")
knockdown_df = df[df["Type of Record"] == "Knockdowns Landed"]
fig7 = px.histogram(knockdown_df, x="Total", title="Distribution of Knockdowns Landed")
plotly(fig7)

# 8. **Decision Wins Breakdown** - Bar Chart
text("## Decision Wins Breakdown")
decision_df = df[df["Type of Record"] == "Decision Wins"]
fig8 = px.bar(decision_df, x="Name", y="Total", color="Name", title="Fighters with Most Decision Wins")
plotly(fig8)

# 9. **Takedowns Landed Per Fighter** - Horizontal Bar Chart
text("## Takedowns Landed Per Fighter")
takedown_landed_df = df[df["Type of Record"] == "Takedowns Landed"]
fig9 = px.bar(takedown_landed_df, x="Total", y="Name", orientation='h', color="Name", title="Most Takedowns Landed in UFC History")
plotly(fig9)

# 10. **Heatmap: Control Time vs. Total Fight Time**
text("## Control Time vs Total Fight Time")
grappling_df = df[df["Type of Record"].isin(["Control Time", "Total Fight Time"])]
fig10 = px.density_heatmap(grappling_df, x="Name", y="Total", title="Control Time vs Total Fight Time")
plotly(fig10)