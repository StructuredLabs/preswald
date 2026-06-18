import pandas as pd
import plotly.express as px

from preswald import plotly, separator, slider, text, text_input, view


# Title
text("# Weather Data")
text("### Ammount of rainfall")

# Get data from the weather.csv file(Not real data, just dummy data to work with.)
df = pd.read_csv("./data/weather.csv")


# Creating a method for creating histograms.
def histogram(data, x_axis, y_axis, color, bins, title, template):
    histogram = px.histogram(
        data,
        x=x_axis,
        y=y_axis,
        color=color,
        nbins=bins,
        title=title,
        template=template,
    )
    return histogram


# Set up percipitation slider, anmd setting max, min, and default values.
min_precipitation = slider(
    "Minimum Precipitation", min_val=0.0, max_val=10.0, default=4.0
)

# Filtering precipitation data based on position of the slider.
filtered_precipitation_data = df[
    df["Precipitation"] >= min_precipitation.get("value", min_precipitation)
].sort_values(by="Precipitation", ascending=False)

# Calling the plotly and histogram functions to display rainfall data.
plotly(
    histogram(
        filtered_precipitation_data,
        "city",
        "Precipitation",
        "city",
        20,
        "Ammount of Rainfall<br> <sup>(Inches)</sup>",
        "plotly_white",
    )
)

separator()

# Creating a mapbox map to display data over a map.
text("### Map of cities with rainfall and temperature stats.")
rain_map = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    hover_data=["Precipitation", "high_temp", "low_temp"],
    color="city",
    zoom=3,
    mapbox_style="open-street-map",
    title="Rainfall Hovermap",
)

# Plotting the map with weather data per city.
plotly(rain_map)

separator()

# Asking the user for input on a city they would like information on.
user_input = text_input(
    label="Input a city you want to see data on.",
    placeholder="Type input carefully, it is case and special character sensetive.",
    size=1.5,
)

# Filtering the users input and returning the city they inputted.
filtered_user_input = df[df["city"] == user_input.get("value", user_input)].sort_values(
    by="city", ascending=False
)

# Viewing data on the inputted users city.
view(filtered_user_input)

separator()

# Sorting the data by high temperatures to show hottest cities.
high_temps = df.sort_values(by="high_temp", ascending=False)

low_temps = df.sort_values(by="low_temp", ascending=True)

# Limiting the number of hottest citites.
limited_high_temps = high_temps.head(5)

# getting the coldest cities
limited_low_temps = low_temps.head(5)

# Displaying the hottest cities in a hiostogram.
text("### Hottest Cities")

plotly(
    histogram(
        limited_high_temps,
        "city",
        "high_temp",
        "city",
        50,
        "Hottest Cities",
        "plotly_white",
    )
)

separator()

# Displaying coldest cities
text("### Coldest Cities")

plotly(
    histogram(
        limited_low_temps,
        "city",
        "low_temp",
        "city",
        50,
        "Coldest Cities",
        "plotly_white",
    )
)

text(
    """This is all example data, and not actual weather data. The examples are based
     off of sample data in the form of a CSV file. Any comparison to actual historic
     weather data is purely coincidental and is not accurate.
"""
)
