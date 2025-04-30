from preswald import text, plotly, connect, get_df, table, query
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Title
text("Football Player Stats Analysis (Top 10 Players)")

connect()
df = pd.read_csv("data/Final_players_stats.csv")

df = df.sort_values(by="Goals", ascending=False).head(10)

### Goals vs. Assists (Top 10 Performers) - Bar Plot with Color Gradient
fig1 = px.bar(df, x="Player", y=["Goals", "Assists"], 
              title="Goals vs. Assists (Top 10 Players)", 
              labels={"Goals": "Total Goals", "Assists": "Total Assists"},
              color="Assists", barmode="group", 
              height=400)
fig1.update_layout(template="plotly_white")
plotly(fig1)

###Pass Completion % vs. Progressive Passes - Box Plot
fig3 = px.box(df, x="Player", y="PasTotCmp%", 
              title="Pass Completion % (Top 10)", 
              labels={"PasTotCmp%": "Pass Completion %"})
fig3.update_layout(template="plotly_white")
plotly(fig3)

### Tackles vs. Interceptions (Defensive Strength) - Radar Chart
fig4 = go.Figure()
for player in df["Player"]:
    player_data = df[df["Player"] == player]
    fig4.add_trace(go.Scatterpolar(
        r=[player_data["Tkl"].values[0], player_data["Int"].values[0]],
        theta=["Tackles", "Interceptions"],
        fill="toself", name=player
    ))

fig4.update_layout(
    title="Defensive Strength (Tackles vs. Interceptions)",
    polar=dict(radialaxis=dict(visible=True, range=[0, max(df["Tkl"].max(), df["Int"].max())])),
    template="plotly_white"
)
plotly(fig4)

### Aerial Duels Won % vs. Total Duels - Bubble Plot
fig5 = px.scatter(df, x="AerWon%", y="AerWon", text="Player", 
                  title="Aerial Duels Won % vs. Total Duels (Top 10)", 
                  labels={"AerWon%": "Aerial Duels Won %", "AerWon": "Total Aerial Duels Won"},
                  size="AerLost", color="AerWon%", 
                  hover_data=["AerLost"])
fig5.update_traces(textposition="top center", marker=dict(opacity=0.7))
fig5.update_layout(template="plotly_white")
plotly(fig5)

### Player Performance vs. Total Goals - Treemap (Hierarchy Visualization)
fig6 = px.treemap(df, path=["Player"], values="Goals", 
                  title="Player Performance vs. Total Goals (Top 10)",
                  color="Assists", hover_data=["SoT%", "PasTotCmp%"],
                  color_continuous_scale="RdBu")
fig6.update_layout(template="plotly_white")
plotly(fig6)


# Display the dataset in a table
table(df)
