from preswald import text, plotly, connect, get_df, table, query, slider
import plotly.express as px

text("# Pokémon Data Explorer")
text("Explore Pokémon statistics with interactive visualizations!")

connect()
df = get_df("pokedex")

df['weight'] = df['weight'].astype(float)
df['attack'] = df['attack'].astype(float)
df['defense'] = df['defense'].astype(float)
df['speed'] = df['speed'].astype(float)

# ─────────────────────────────────────────────────────────
text("## Scatter Plot: Weight vs Attack Power")
attack_threshold = slider("Min Attack Power", min_val=df['attack'].min(), max_val=df['attack'].max(), default=50)

scatter_query = f"SELECT * FROM pokedex WHERE attack >= {attack_threshold}"
filtered_scatter_df = query(scatter_query, "pokedex")

fig1 = px.scatter(filtered_scatter_df, x='weight', y='attack', text='name',
                   title='Weight vs. Attack Power',
                   labels={'weight': 'Weight (kg)', 'attack': 'Attack Power'},
                   hover_name='name', color='speed')

fig1.update_traces(textposition='top center', marker=dict(size=10))
fig1.update_layout(template='plotly_white')

plotly(fig1)

# ─────────────────────────────────────────────────────────
text("## Bar Chart: Top Pokémon by Attack Power")
top_n_attack = slider("Number of Pokémon", min_val=5, max_val=20, default=10)

bar_query = f"SELECT * FROM pokedex ORDER BY attack DESC LIMIT {top_n_attack}"
filtered_bar_df = query(bar_query, "pokedex")

fig2 = px.bar(filtered_bar_df, x="name", y="attack", color="defense",
              title=f"Top {top_n_attack} Pokémon by Attack Power",
              labels={"attack": "Attack Power", "defense": "Defense"},
              text_auto=True)

fig2.update_layout(template="plotly_white")

plotly(fig2)

# ─────────────────────────────────────────────────────────
text("## Scatter Plot: Speed vs Attack Power")
speed_threshold = slider("Min Speed", min_val=df['speed'].min(), max_val=df['speed'].max(), default=30)

speed_query = f"SELECT * FROM pokedex WHERE speed >= {speed_threshold}"
filtered_speed_df = query(speed_query, "pokedex")

fig3 = px.scatter(filtered_speed_df, x='speed', y='attack', text='name',
                   title='Speed vs. Attack Power',
                   labels={'speed': 'Speed', 'attack': 'Attack Power'},
                   hover_name='name', color='defense')

fig3.update_traces(textposition='top center', marker=dict(size=10))
fig3.update_layout(template='plotly_white')

plotly(fig3)

# ─────────────────────────────────────────────────────────
text("## Bar Chart: Average Attack Power by Pokémon Type")
type_attack_threshold = slider("Min Average Attack", min_val=df['attack'].min(), max_val=df['attack'].max(), default=40)

type_attack_query = f"""
    SELECT type, AVG(attack) as avg_attack FROM pokedex 
    GROUP BY type HAVING avg_attack >= {type_attack_threshold}
"""
filtered_type_attack_df = query(type_attack_query, "pokedex")

fig4 = px.bar(filtered_type_attack_df, x="type", y="avg_attack", color="avg_attack",
              title="Average Attack Power by Pokémon Type",
              labels={"avg_attack": "Average Attack"},
              text_auto=True)

fig4.update_layout(template="plotly_white")

plotly(fig4)

# ─────────────────────────────────────────────────────────
text("## Scatter Plot: Weight vs Speed (Grouped by Pokémon Type)")
weight_threshold = slider("Min Weight", min_val=df['weight'].min(), max_val=df['weight'].max(), default=50)

type_weight_query = f"SELECT * FROM pokedex WHERE weight >= {weight_threshold}"
filtered_type_weight_df = query(type_weight_query, "pokedex")

fig5 = px.scatter(filtered_type_weight_df, x='weight', y='speed', text='name',
                   title='Weight vs. Speed by Pokémon Type',
                   labels={'weight': 'Weight (kg)', 'speed': 'Speed'},
                   hover_name='name', color='type')

fig5.update_traces(textposition='top center', marker=dict(size=10))
fig5.update_layout(template='plotly_white')

plotly(fig5)


table(filtered_scatter_df.head(20), title="Filtered Pokémon Data (First 20 Rows)")
