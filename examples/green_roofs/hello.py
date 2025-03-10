from preswald import text, plotly, connect, get_df, table
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd

text("# Green Roofs in San Francisco")
text("## Analyzing Trends in Green Roof Maintenance and Installation")

# Load the CSV
connect()
df = get_df('Green_Roofs')

gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df['the_geom']))

gdf['lat'] = gdf.geometry.y
gdf['lon'] = gdf.geometry.x

gdf['ConstrType'] = gdf['ConstrType'].fillna("Unknown")
gdf['YearBuilt'] = pd.to_numeric(gdf['YearBuilt'], errors='coerce')
gdf['YearBuilt'] = gdf['YearBuilt'].fillna(0).astype(int)

## types building usage (residential, commercial, industrial, etc.)
building_u_counts = gdf['Building_U'].value_counts().reset_index()
building_u_counts.columns = ['Building_U', 'Count']

## pie chart
building_u_pie = go.Pie(
    labels=building_u_counts['Building_U'],
    values=building_u_counts['Count'],
    name='Building Usage Pie Chart',
    visible=True ## start with pie chart
)
## bar chart
building_u_bar = go.Bar(
    x=building_u_counts['Building_U'],
    y=building_u_counts['Count'],
    name='Building Usage Bar Chart',
    visible=False
)

building_u_figure = go.Figure()

building_u_figure.add_trace(building_u_pie)
building_u_figure.add_trace(building_u_bar)
building_u_figure.update_traces(
    visible=False, 
    selector=dict(name="Categories of Green Roof Installed Buildings"))

## buttons to toggle between pie chart and bar chart
building_u_figure.update_layout(
    updatemenus=[
        {
            "buttons": [
                {
                    "label": "Pie Chart",
                    "method": "update",
                    "args": [{"visible": [True, False]}, {"title": "Building Buildings Uses"}],
                },
                {
                    "label": "Bar Chart",
                    "method": "update",
                    "args": [{"visible": [False, True]}, {"title": "Buildings Uses"}],
                }
            ],
            "direction": "down",
            "showactive": True,
        }
    ]
)


## remove unifinished buildings (YearBuilt == 0)
filtered_yearly_data = gdf[gdf['YearBuilt'] != 0]
yearly_data = filtered_yearly_data.groupby('YearBuilt').size().reset_index(name='Installations')

## there's only one buildling installed per year before 2005 so removing it for better visualization
yearly_data = yearly_data[yearly_data['YearBuilt'] >= 2005]

yearly_trend = px.line(yearly_data, x="YearBuilt", y="Installations",
               labels={"YearBuilt": "Year", "Installations": "Number of Installations"})

yearly_trend.update_layout(xaxis=dict(range=[yearly_data['YearBuilt'].min(), yearly_data['YearBuilt'].max()],tickmode='linear'))

## plot map of all (recorded) green roofs in San Francisco
roof_map = go.Figure(go.Scattermapbox(
    lat=gdf['lat'],
    lon=gdf['lon'],
    mode='markers',
    marker=dict(size=10, color='green'),
    text=gdf['Building_N'] + "<br>" + gdf['ADDRESS'],
))

roof_map.update_layout(
    mapbox_style="carto-positron",
    mapbox_center={"lat": 37.7749, "lon": -122.4194},
    mapbox_zoom=12
)

# Show all the plots
text ("### Buildings Types of Green Roof Installations")
plotly(building_u_figure)

text ("### Yearly Trend of Green Roof Installations")
plotly(yearly_trend)

text ("### Map of Green Roofs in San Francisco")
plotly(roof_map)

text ("### Raw Data")
table(gdf)