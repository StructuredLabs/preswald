import preswald as pw
import pandas as pd
import plotly.express as px
from preswald.engine.service import PreswaldService

pw.text("# Weather Data Visualization")
pw.text("## Explore temperature extremes in daily weather data")


pw.connect()
df = pw.get_df('weather_csv')

df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
df["year"] = df["date"].dt.year.astype(str)
df["day_month"] = df["date"].dt.strftime("%d-%m-00") 


service = PreswaldService.get_instance()


selected_country = pw.selectbox("Select Country", options=df["country"].unique().tolist())
filtered_df = df[df["country"] == selected_country]
selected_city = pw.selectbox("Select City", options=filtered_df["city"].unique().tolist())
selected_years = []
for year in sorted(df["year"].unique().tolist()):
    cb = pw.checkbox(f"Select Year {year}", default=False)
    if cb:
        selected_years.append(year)


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



    return fd_min, fd_max


def update_plots():
    min_temp_df, max_temp_df = reshape_data()

    if min_temp_df is None or max_temp_df is None:
        return


    fig = px.line(
        min_temp_df,
        x="day_month",
        y=selected_years,
        title="...",
        labels={"value": "Min Temperature (°C)", "day_month": "Date (dd-mm)"}
    )
    fig.update_xaxes(type="category")
    service.append_component(pw.plotly(fig)) 

    fig = px.line(
        max_temp_df,
        x="day_month",
        y=selected_years,
        title="...",
        labels={"value": "Max Temperature (°C)", "day_month": "Date (dd-mm)"}
    )
    fig.update_xaxes(type="category")
    service.append_component(pw.plotly(fig)) 

service.append_component(pw.button("Update Plots", size=1.0))
update_plots()
