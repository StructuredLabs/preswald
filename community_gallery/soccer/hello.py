from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = pd.read_csv('data/players2.csv', delimiter=';')  


# Create a scatter plot
positions = df['club_position'].value_counts().index[:3]  
df_filtered = df[df['club_position'].isin(positions)]  

# 1. Histogram for Dribbling Skills Distribution by Position
fig1 = px.histogram(
    df_filtered,
    x="dribbling",  
    color="club_position",  
    labels={"dribbling": "Dribbling Skill Level"},
    nbins=20  
)

fig1.update_layout(template="plotly_white", title_font_size=36, 
                  xaxis_title="Dribbling Skill Level", yaxis_title="Frequency")

# 2. Scatter Plot for Shot Power vs. Sprint Speed by Age
fig2 = px.scatter(
    df_filtered,
    x="shot_power",  
    y="sprint_speed",  
    color="age",  
    labels={"shot_power": "Shot Power Skill Level", "sprint_speed": "Sprint Speed (Pace)"},
    color_continuous_scale='Viridis'
)

fig2.update_traces(textposition="top center", marker=dict(size=12))
fig2.update_layout(template="plotly_white", title_font_size=36, 
                  xaxis_title="Shot Power Skill Level", yaxis_title="Sprint Speed (Pace)")

# 3. Bar Chart for Top 10 Countries by Player Count
country_distribution = df['country'].value_counts().head(10).reset_index()  
country_distribution.columns = ['Country', 'Player Count']

fig3 = px.bar(
    country_distribution,
    x="Country",
    y="Player Count",
    labels={"Country": "Country", "Player Count": "Number of Players"},
    color='Player Count',
    color_continuous_scale='Blues'
)

fig3.update_layout(template="plotly_white", title_font_size=36, 
                  xaxis_title="Country", yaxis_title="Number of Players")

text("## Distribution of Dribbling Skills by Position 🏅")
plotly(fig1)
text("## Shot Power vs Sprint Speed by Age 💥💨")
plotly(fig2)
text("## Top 10 Countries by Player Count 🌍")
plotly(fig3)
