from preswald import text, plotly, connect, get_df, table, query, slider
import plotly.express as px

text("# Pokémon Stats Analysis!")
text("Explore relationships in Pokémon attributes. 🎮")

# Load the CSV
connect()  # load in all sources, which by default is the sample_csv
df = get_df("pokedex_csv")

# Create a scatter plot
fig = px.scatter(
    df,
    x="attack",
    y="defense",
    color="type",
    hover_name="name",
    title="Attack vs Defense by Pokémon Type",
    labels={"attack": "Attack Stat", "defense": "Defense Stat"},
    hover_data=["hp", "weight", "evo_set"],
)


# Add labels for each point
fig.update_traces(textposition="top center", marker=dict(size=12, color="lightblue"))

# Style the plot
fig.update_layout(template="plotly_white")

# Show the plot
plotly(fig)

# Show the data
table(df)

# Filter the data based off the threshold
threshold = slider("Attack Threshold", min_val=0, max_val=180, default=50)
text(f"### Pokémon with Attack > {threshold}")
dynamic_df = df[df["attack"] > threshold]
table(dynamic_df, title="Attack Filtered Data")


# Query the data
text("## Elite Defender Query")
sql = """SELECT name, type, attack, defense, speed 
         FROM pokedex_csv 
         WHERE attack > 120 AND defense > 100 
         ORDER BY attack + defense DESC"""
filtered_df = query(sql, "pokedex_csv")
text("### Top Balanced Fighters (Attack > 120 & Defense > 100)")
table(filtered_df, title="Elite Pokémon Metrics")
