from preswald import text, plotly, connect, get_df, table, checkbox, slider
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from sklearn import preprocessing
import plotly.io as pio
import plotly.graph_objects as go
import numpy as np


connect()

text("# Welcome to the US Aviation Analysis App!")

df = pd.read_csv("./data/sample.csv")

text("", size=.15)
year = slider(
    label="Select Year",
    min_val=1996,
    max_val=2024,
    step=1,
    default=2005,
    size=.7
)
text("", size=.15)


df_year = df[df["Year"] == year]

# Passenger data visualization

df_temp = df_year.groupby("city_cleaned", as_index=False).agg({
    "ly_passengers": "sum",  
    "longitude": "first",  
    "latitude": "first",
    # "Year": "first"
})

df_temp["ly_passengers"] = df_temp["ly_passengers"] / 1_000_000
df_temp["Total Passengers"] = df_temp["ly_passengers"].apply(lambda x: f"{x:.2f} x 10^6")

fig1 = px.scatter_geo(df_temp, lat='latitude', lon='longitude', size="ly_passengers", 
                     hover_name="city_cleaned", hover_data={"latitude": False, "longitude": False,"Total Passengers":True, "ly_passengers":False}, title=f"<b>Passenger Traffic at US airports in {year}</b>",
                     projection="albers usa", scope="usa",
                     color_continuous_scale="Viridis", size_max=60)

# df_pass = df.groupby(["Year", "city_cleaned"], as_index=False).agg({
#     "ly_passengers": "sum", 
#     "latitude": "first", 
#     "longitude": "first",
# })

# df_pass = df_pass.sort_values(by=["Year"], ascending=[True])

# fig1 = px.scatter_geo(df_pass, lat='latitude', lon='longitude', size="ly_passengers", 
#                      hover_name="city_cleaned", hover_data={"latitude": False, "longitude": False,"Total Passengers":True, "ly_passengers":False}, title=f"Passenger Traffic at US airports Over Time",
#                      projection="albers usa", scope="usa", animation_frame="Year", 
#                      color_continuous_scale="Viridis", size_max=60)

plotly(fig1)

# # Show the plot
# pio.to_html(fig1, full_html=False, auto_play=True)
# pio.show(fig1)

# 3D plot

df_temp = df.groupby("city_cleaned", as_index=False).agg({
    "ly_passengers": "sum",
    "ly_fare": "sum", 
    "distance": "sum"
})

df_temp["Number of Passengers"] = df_temp["ly_passengers"] / 1_000_0000
df_temp["Avg Fare"] = df_temp["ly_fare"] / 1_000
df_temp["Avg Distance of flights"] = df_temp["distance"] / 1000

df_temp["pass_label"] = df_temp["Number of Passengers"].apply(lambda x: f"{x:.2f} x 10^6")
df_temp["fare_label"] = df_temp["Avg Fare"].apply(lambda x: f"{x:.2f} x 10^3")
df_temp["dist_label"] = df_temp["Avg Distance of flights"].apply(lambda x: f"{x:.2f} x 10^3")

df_temp['color'] = np.random.choice([1, 2, 3], size=len(df_temp), p=[0.33, 0.33, 0.34])

fig2 = px.scatter_3d(df_temp, x='Avg Fare', y='Number of Passengers', z='Avg Distance of flights', size='Avg Fare',
                     hover_name='city_cleaned', hover_data={"pass_label":True, "fare_label":True, "dist_label":True, "Number of Passengers":False, "Avg Fare":False, "Avg Distance of flights":False}, title='<b>City-wise Comparison: Fare, Yield, and Distance</b>', size_max=50, color="color",)
fig2.update_layout(scene_camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)))

plotly(fig2)

# Fare data visualization

df_temp = df.groupby("Year", as_index=False).agg({
    "ly_fare": "sum",
    "cur_fare": "sum"
})

df_temp["cur_fare"] = df_temp["cur_fare"] / 1000
df_temp["ly_fare"] = df_temp["ly_fare"] / 1000

fig3 = px.line(df_temp, x="Year", y=["cur_fare", "ly_fare"], title='<b>Air Fares in the US Over Time</b>', markers=True)

plotly(fig3)

