from preswald import text, plotly, connect, get_df
import plotly.express as px
import plotly.graph_objects as go

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('pokedex_csv')

text("# pokemon dashboard <3")
text("## made by amruth niranjan")
text("explore the world of pokemon!")


# redo the "types" --> for example, "fire/flying" should count for both fire and flying individually
# types is structured as a set of strings
# create a new column called "type_1" and "type_2"
df['type_1'] = df['type'].apply(lambda x: x.strip('{}').split(',')[0].strip())
df['type_2'] = df['type'].apply(lambda x: x.strip('{}').split(',')[1].strip() if len(x.strip('{}').split(',')) > 1 else '')
df['type_2'] = df['type_2'].fillna('')

df['type'] = df['type_1']


df = df.drop(columns=['type'])

# now, get type distribution: anything with fire should count for fire, anything with flying should count for flying, etc.

type_counts = df['type_1'].value_counts()
type_counts_2 = df['type_2'].value_counts()

type_dist = type_counts.add(type_counts_2, fill_value=0)

type_dist = type_dist.drop(index='') # removes "typeless"

text("## physical stats comparison")
# we want to show both types for color
fig_stats = px.scatter(df, 
                      x='attack', 
                      y='defense',
                      size='hp',
                      color='type_1',
                      symbol='type_2',
                      hover_data=['name', 'hp', 'speed'],
                      title='physical stats: attack vs defense (sized by hp)')


plotly(fig_stats)




text("## special stats comparison")
s_fig_stats = px.scatter(df, 
                      x='s_attack', 
                      y='s_defense',
                      size='hp',
                      color='type_1',
                      symbol='type_2',
                      hover_data=['name', 'hp', 'speed'],
                      title='special stats: special attack vs special defense (sized by hp)')
plotly(s_fig_stats)

# Type distribution
text("## pokemon type distribution")



fig_types = px.pie(values=type_dist.values, 
                   names=type_dist.index,
                   title='distribution of pokemon types... the colors are a bit off!')
plotly(fig_types)



poke = df.sample(1).iloc[0]

text("## random pokemon stats radar chart!")
text(f"### now displaying the stats for: {poke['name']}!")

fig = go.Figure()

fig.add_layout_image(
    dict(
        source=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{poke['id']}.png",
        xref="paper",
        yref="paper",
        x=0.5,  
        y=0.5,  
        sizex=0.5,  
        sizey=0.5,  
        sizing="contain", 
        layer="below"
    )
)

fig.update_layout(
    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False,),
    yaxis=dict(showgrid=False, showticklabels=False, zeroline=False,),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0, r=0, t=0, b=0), 
    width=300, 
    height=300  
)

plotly(fig) 
# Use Charizard as an example
stats = ['hp', 'attack', 'defense', 's_attack', 's_defense', 'speed']
values = [poke[stat] for stat in stats]

fig_radar = go.Figure()

fig_radar.add_trace(go.Scatterpolar(
    r=values,
    theta=stats,
    fill='toself',
    name=f'{poke["name"]}'
))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 255]
        )),
    showlegend=False,
    title=f'{poke["name"]} base stats'
)

plotly(fig_radar)

# Pokemon descriptions
text("## pokemon descriptions")
text("here are some interesting pokemon descriptions:")

sample_descriptions = df.sample(3)
for _, pokemon in sample_descriptions.iterrows():
    

    text(f"### {pokemon['name']}")
    text(f"*{pokemon['info']}*")

    fig = go.Figure()

    fig.add_layout_image(
        dict(
            source=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon['id']}.png",
            xref="paper",
            yref="paper",
            x=0.5,  
            y=0.5,  
            sizex=0.5,  
            sizey=0.5,  
            sizing="contain", 
            layer="below"
        )
    )

    fig.update_layout(
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False,),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False,),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0), 
        width=300, 
        height=300  
    )

    plotly(fig) 
    text("---")

# height vs weight scatter plot
text("## pokemon size comparison")
fig_size = px.scatter(df,
                     x='height',
                     y='weight',
                     color='type_1',
                     symbol='type_2',
                     hover_data=['name'],
                     title='pokemon height vs weight by type')
plotly(fig_size) 