import pandas as pd
import plotly.express as px

df = pd.read_csv('data/sample.csv')

# Geographic Scatter Plot
fig = px.scatter_geo(df,
    lat="decimalLatitude",
    lon="decimalLongitude",
    hover_name="speciesQueried",
    color="country",
    title="Geographical Distribution of Callitrichidae Specimens",
    projection="natural earth"
)

# Density Heatmap
hotspot_map = px.density_mapbox(
    df,
    lat="decimalLatitude",
    lon="decimalLongitude",
    radius=8,
    zoom=3,
    color_continuous_scale="Viridis",
    mapbox_style="carto-positron",
    title="Spatial Density Analysis of Callitrichidae Populations"
)

# Species Richness Analysis
richness = df.groupby("country")["speciesQueried"].nunique().reset_index(name="richness")
richness_plot = px.bar(
    richness.sort_values("richness", ascending=False),
    x="country",
    y="richness",
    title="Callitrichidae Species Richness by Geographic Region"
)

# Hierarchical Distribution Analysis
df_treemap = df.groupby(["country", "speciesQueried"]).size().reset_index(name="count")
treemap_plot = px.treemap(
    df_treemap,
    path=["country", "speciesQueried"],
    values="count",
    color="count",
    title="Taxonomic and Geographic Distribution of Callitrichidae Specimens"
)

# Life Stage Temporal Analysis
life_stage_trend = df[df["lifeStage"].notna() & (df["lifeStage"].str.lower() != "unknown")]
life_stage_plot_data = life_stage_trend.groupby(["year", "lifeStage"]).size().reset_index(name="count")
life_stage_plot = px.line(
    life_stage_plot_data,
    x="year",
    y="count",
    color="lifeStage",
    title="Ontogenetic Distribution of Callitrichidae Observations: Temporal Analysis"
)

# Displays
import preswald

preswald.text("# Biogeographical Analysis of Callitrichidae Distribution Patterns")

preswald.text("## Spatial Distribution Analysis")
preswald.text("Figure 1 illustrates the geographical distribution of Callitrichidae specimens across their native range. Individual data points represent documented occurrences, with color differentiation by country to facilitate identification of biogeographical patterns and potential ecological niches.")
preswald.plotly(fig)

preswald.text("## Population Density Assessment")
preswald.text("Figure 2 presents a kernel density estimation of Callitrichidae observations, highlighting regions of significant population concentration. This visualization aids in identifying critical habitat zones and potential conservation priority areas for these neotropical primates.")
preswald.plotly(hotspot_map)

preswald.text("## Species Richness Evaluation")
preswald.text("Figure 3 quantifies Callitrichidae taxonomic diversity across political boundaries. This analysis reveals significant variation in species richness among countries, potentially reflecting both natural biogeographical patterns and sampling bias considerations.")
preswald.plotly(richness_plot)

preswald.text("## Taxonomic Distribution by Geographic Region")
preswald.text("Figure 4 depicts the hierarchical relationship between geographic distribution and taxonomic classification within the Callitrichidae family. The proportional representation illustrates both abundance and diversity patterns across the study area, with implications for understanding evolutionary and ecological relationships.")
preswald.plotly(treemap_plot)

preswald.text("## Ontogenetic Temporal Distribution")
preswald.text("Figure 5 examines the temporal distribution of Callitrichidae specimens across different life stages. This longitudinal analysis may reveal important demographic shifts, reproductive patterns, or methodological biases in data collection that warrant further investigation.")
preswald.plotly(life_stage_plot)