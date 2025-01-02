from preswald import text, connect, view, slider, plotly, connections, checkbox, button, selectbox, text_input, progress, spinner, alert, image

from sqlalchemy import text as sql_text
import pandas as pd
import plotly.express as px

# Title
text("# Earthquake Analytics Dashboard 🌍")

show_map = checkbox("Show Map", default=True)
# button_val = button("Run")
selectbox_val = selectbox("Select a country", options=["USA", "Canada", "UK", "Australia"])
text_input_val = text_input("Enter your name")
# progress_val = progress("Loading data", value=0.5)
# spinner_val = spinner("Spinning...")
# alert_val = alert("This is an alert message")
# image_val = image("https://via.placeholder.com/150")

# Load and connect data
connection_name = connect("/Users/jayanth.kumar/Downloads/work/structuredLabs/preswald/examples/earthquake_data.csv", "earthquake_connection")

# psql_connection_name = connect("postgresql://iris_user:IrisUser%40123@34.171.68.74/iris_database", "psql_connection")

# Slider for filtering magnitude
# here min_magnitude is {'type': 'slider', 'id': 'slider-f6dab796', 'label': 'Minimum Magnitude', 'min': 0.0, 'max': 10.0, 'step': 1, 'value': 5.0}
min_magnitude = slider("Minimum Magnitude", min_val=0.0,
                       max_val=10.0, default=5.0)

# Read the data and filter based on magnitude
data = pd.DataFrame(connections[connection_name])
# Convert Magnitude column to numeric, handling any non-numeric values
data['Magnitude'] = pd.to_numeric(data['Magnitude'], errors='coerce')
filtered_data = data[data['Magnitude'] >=
                     min_magnitude.get('value', min_magnitude)]

# Summary statistics
text(f"### Total Earthquakes with Magnitude ≥ {min_magnitude.get('value', min_magnitude)}: {len(filtered_data)}")

text(f'selected value from the box: {selectbox_val.get("value", selectbox_val)}')

# Interactive map using Plotly

if show_map.get('value', show_map):
    text("## Earthquake Locations")
    fig_map = px.scatter_geo(
        filtered_data,
        lat='Latitude',
        lon='Longitude',
        color='Magnitude',
        size='Magnitude',
        hover_name='ID',
        title="Earthquake Map"
    )
    plotly(fig_map)

# Magnitude distribution
fig_hist = px.histogram(
    filtered_data,
    x="Magnitude",
    nbins=20,
    title="Distribution of Magnitudes"
)
plotly(fig_hist)

# Depth vs. Magnitude scatter plot
fig_scatter = px.scatter(
    filtered_data,
    x="Depth",
    y="Magnitude",
    color="Magnitude",
    title="Depth vs Magnitude",
    labels={"Depth": "Depth (km)", "Magnitude": "Magnitude"}
)
plotly(fig_scatter)

# engine = connections[psql_connection_name]
# result = None
# with engine.connect() as connection:
#     query = sql_text("SELECT * FROM iris")
#     result = connection.execute(query)

# text(str(result.fetchall()))
view(connection_name)
# view(psql_connection_name)