import preswald as pw
import pandas as pd
import sqlite3
import plotly.express as px
from preswald.engine.service import PreswaldService

pw.text("# Weather Data Visualization")
pw.text("## Explore temperature extremes in daily weather data")

# Load dataset
pw.connect()
df = pw.get_df('weather_csv')

df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
df["year"] = df["date"].dt.year.astype(str)  # Ensure year is categorical
df["day_month"] = df["date"].dt.strftime("%d-%m-00")  # Pre-computed column

# Initialize Preswald Service
service = PreswaldService.get_instance()

# UI Components
selected_country = pw.selectbox("Select Country", options=df["country"].unique().tolist())
filtered_df = df[df["country"] == selected_country]
selected_city = pw.selectbox("Select City", options=filtered_df["city"].unique().tolist())
selected_years = []
for year in sorted(df["year"].unique().tolist()):
    cb = pw.checkbox(f"Select Year {year}", default=False)
    if cb:
        selected_years.append(year)

# Function to reshape data
def reshape_data():
    city = selected_city
    years = selected_years

    if not city or not years:
        return None, None

    filtered_data = df[(df["city"] == city) & (df["year"].isin(years))].copy()
    unique_dates = sorted(filtered_data["day_month"].unique())

    fd_min = pd.DataFrame({"day_month": unique_dates})
    fd_max = pd.DataFrame({"day_month": unique_dates})

    for y in years:
        yearly_data = filtered_data[filtered_data["year"] == y].set_index("day_month")
        fd_min[y] = fd_min["day_month"].map(yearly_data["tmin"].to_dict())
        fd_max[y] = fd_max["day_month"].map(yearly_data["tmax"].to_dict())

    # fd_min.columns = fd_min.columns.astype(str)
    # fd_max.columns = fd_max.columns.astype(str)

    return fd_min, fd_max

# Function to update plots
def update_plots():
    min_temp_df, max_temp_df = reshape_data()

    if min_temp_df is None or max_temp_df is None:
        return

    # Melt dataframes for plotly
    fig = px.line(
        min_temp_df,
        x="day_month",
        y=selected_years,  # Plot all year columns directly
        title="...",
        labels={"value": "Min Temperature (°C)", "day_month": "Date (dd-mm)"}
    )
    fig.update_xaxes(type="category")
    service.append_component(pw.plotly(fig)) 

# Assemble UI
service.append_component(pw.button("Update Plots", size=1.0))
update_plots()
