from preswald import text, plotly, connect, get_df, selectbox
import plotly.express as px
import plotly.graph_objects as go

text("# Get Data about Electric Vehicle in Washington DC")

# Load the CSV
connect()  # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')

# Graph showing state with most vehicles
text("Which State had the most electric vehicles")
state_counts = df["City"].value_counts().reset_index()
state_counts.columns = ["City", "Number of Vehicles"]
city_options = ["All"] + [5,10,15, 20, 25, 50]
selected_top_n = selectbox("Select a City", options=city_options)
if selected_top_n == "All":
    top_cities = state_counts
else:
    top_cities = state_counts.nlargest(selected_top_n, "Number of Vehicles")
bar_fig = px.bar(top_cities, x="City", y="Number of Vehicles", title=f'Top {selected_top_n} Cities by Number of Electric Vehicles')
plotly(bar_fig)


# Pie chart showing Make with most vehicles
text("Distribution of Electric Vehicle Brands")
make_counts = df["Make"].value_counts().reset_index()
make_counts.columns = ["Make", "Number of Appearances"]
# Create a dropdown for selecting the number of top brands
brand_options = [5, 10, 15, 20]
selected_brand_n = selectbox("Select number of top brands to display", options=brand_options)
# Filter the data based on the selected number of top brands
filtered_make_counts = make_counts.nlargest(selected_brand_n, "Number of Appearances")
pie_fig = px.pie(filtered_make_counts, values="Number of Appearances",
                 names="Make", title="Distribution")
plotly(pie_fig)

# Geo chart showing the location of the Electric vehicle
text("Geo chart showing the location of each vehicle")
df[["Longitude", "Latitude"]] = df["Vehicle Location"].str.extract(
    r'POINT \(([-\d.]+) ([-\d.]+)\)')
dc_lat = 38.9072
dc_lon = -77.0369
figure = go.Figure()
top_cities = df["City"].value_counts().nlargest(10).index.tolist()
options = ["All"] + top_cities
selected_city = selectbox(
    "Pick a city in Washington",
    options=options,
    default="All"
)
if selected_city == "All":
    filtered_geo_df = df
else:
    filtered_geo_df = df[df["City"] == selected_city]

figure.add_trace(go.Scattergeo(
    lon=filtered_geo_df["Longitude"],
    lat=filtered_geo_df["Latitude"],
    text=filtered_geo_df["Make"],
    mode='markers',
    marker=dict(
        size=5,
        color='black',
        symbol='diamond'
    ),
    name=""
))
# prswld-b0a7116a-ed35-46d2-9820-bbf418a37a83
# Adjust the layout
figure.update_layout(
    geo=dict(
        center=dict(lat=47.7511, lon=-120.7401),
        projection_scale=30,  # Zoom level
        bgcolor='#f9f9f9',  # Light gray paper background
    ),
)
plotly(figure)

text("Comparison of the Make vs Electric Range")
top_options = [10, 25, 100]
selected_top_n = selectbox("Select number of top entries to display", options=top_options)
top_counties = df.groupby("Make")["Electric-Range"].mean().nlargest(selected_top_n).reset_index()
bar_fig = px.bar(top_counties, x="Make", y="Electric-Range", title=f'Top {selected_top_n} Makes by Electric Range')
plotly(bar_fig)