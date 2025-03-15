import plotly.express as px

from preswald import connect, get_df, plotly, selectbox, text


connect()

# ------------
# Process Data
# ------------

# Get and process dataset for mine locations
minesDf = get_df("mines_csv")
minesDf = minesDf[
    (minesDf["LAT"] != 0) & (minesDf["LONG"] != 0)
]  # Filter entries with invalid cords.

# Get and process dataset for deaths funded by diamonds
deathsDf = get_df("deaths_csv")
deathsDf["War-related deaths"] = (
    deathsDf["War-related deaths"].str.replace(",", "").astype(float)
)  # format numbers
deathsDf = deathsDf[(deathsDf["War-related deaths"] > 5000)]  # Remove small data points
deathsDf = deathsDf[
    deathsDf["Major rebel funding sources"].str.contains(
        "diamonds", case=False, na=False
    )
]  # Retrieve only datapoints where military group's funding source includes diamonds
deathsDf["Conflict"] = (
    deathsDf["Country"] + " (" + deathsDf["Years"] + ")"
)  # Create readable conflict names

# ---------
# Plot Data
# ---------

text(
    "# Conflict Rocks \n TraxNYC, a jeweler from New York City's diamond district, claims that diamond procurement could be ethical by cutting out the middleman. But what does the data say? I used Preswald to map diamond mines and the conflicts they've funded. Here's what the data reveals."
)

# country names from 'deathsDf' mapped to density mapbox configuration values
country_zoom = {
    "Sierra Leone": {"lat": 8.5, "lon": -11.5, "zoom": 6},
    "DRC": {"lat": -4.0, "lon": 21.0, "zoom": 5},
    "Angola": {"lat": -12.0, "lon": 18.0, "zoom": 5},
    "Liberia": {"lat": 7.33, "lon": -10.47, "zoom": 6},
    "All": {"lat": 8, "lon": 20, "zoom": 1},
}

selected_country = selectbox(
    label="Zoom to Country", options=list(country_zoom.keys()), default="All"
)

center = {
    "lat": country_zoom[selected_country]["lat"],
    "lon": country_zoom[selected_country]["lon"],
}

zoom_level = country_zoom[selected_country]["zoom"]

fig_map = px.density_mapbox(
    minesDf,
    title="Global Diamond Mining Activity",
    lat="LAT",
    lon="LONG",
    radius=10,
    center=center,
    zoom=zoom_level,
    mapbox_style="carto-darkmatter",
    hover_data={"COUNTRY": True, "LAT": True, "LONG": True},
    height=800,
)

fig_map.add_annotation(
    text='Source: <a href="https://www.prio.org/data/10" target="_blank">Gilmore et al. (2005)</a>',
    showarrow=False,
    xref="paper",
    yref="paper",
    x=0,
    y=1,
    font=dict(size=12, color="white"),
)

plotly(fig_map)

text(
    "The data shows mine clusters in West Africa, where millions were killed by military groups funded by those same gems. TraxNYC argues that direct sourcing helps miners, not militias. But does it?"
)

fig = px.bar(
    deathsDf,
    x="Conflict",
    y="War-related deaths",
    color="Country",
    hover_data=["Years", "Major rebel funding sources"],
    title="Deaths in Diamond-Funded Conflicts",
    labels={
        "War-related deaths": "War-Related Deaths",
        "Conflict": "Conflict (Country & Years)",
    },
    text_auto=True,
)

fig.update_traces(textposition="outside")

fig.update_layout(
    xaxis_title="Conflict",
    yaxis_title="War-Related Deaths",
    xaxis_tickangle=-45,
    height=600,
    annotations=[
        dict(
            text='Source: <a href="https://www.prio.org/data/10" target="_blank">Lacina, B. & Gleditsch, N.P. (2005)</a>',
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0,
            y=1,
            font=dict(size=12),
        )
    ],
)

plotly(fig)

text(
    'TraxNYC claims that "ethical" business practices can end years of exploitation, but the data suggests a much larger problem. The history suggests that the rocks extracted from these mines have helped raise armies, not people out of poverty.'
)
