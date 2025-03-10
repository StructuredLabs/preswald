from preswald import text, plotly, connect, get_df, table
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd

text("# Green Roofs in San Francisco")
text("Analyzing Trends in Green Roof Maintenance and Installation")

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

sorted_building_u = building_u_counts.sort_values(by='Count', ascending=False)['Building_U']

building_t = px.bar(gdf, x="Building_U", color="ConstrType", 
              title="Building Types by Building Use",
              labels={"Building_U": "Building Use", "ConstrType": "Building Type"},
              category_orders={"Building_U": sorted_building_u.tolist()},
              barmode="stack")

## remove unifinished buildings (YearBuilt == 0)
filtered_yearly_data = gdf[gdf['YearBuilt'] != 0]
yearly_data = filtered_yearly_data.groupby('YearBuilt').size().reset_index(name='Installations')

yearly_trend = px.line(yearly_data, x="YearBuilt", y="Installations", 
               title="Yearly Trend of Green Roof Installations", 
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
    mapbox_zoom=12,
    title="Green Roofs in San Francisco"
)

## finished vs unfinished buildings
gdf['Building_Status'] = gdf['YearBuilt'].apply(lambda x: 'Built' if x != 0 else 'Unfinished')
status_counts = gdf.groupby(['Building_U', 'Building_Status']).size().reset_index(name='Count')
building_status = px.bar(status_counts, x="Building_U", y="Count", color="Building_Status", 
              title="Built vs Unfinished Buildings by Building Use",
              labels={"Building_U": "Building Use", "Count": "Count of Buildings"},
              category_orders={"Building_U": sorted(gdf["Building_U"].unique())},
              barmode="stack")



# Show all the plots
plotly(building_t)
plotly(yearly_trend)
plotly(roof_map)
plotly(building_status)