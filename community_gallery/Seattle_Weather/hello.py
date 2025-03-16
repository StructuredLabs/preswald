"""
Seattle Weather Dashboard
Author: Jayneel Shah (jayneel-shah18)
Date: 03/15/2025
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from preswald import connect, get_df, plotly, slider, table, text


text("# Seattle Weather Dashboard")
text("### Interactive Analysis of Seattle Weather Patterns")

connect()
df = get_df("seattle_weather_csv")

df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y")
df["month"] = df["date"].dt.month
df["month_name"] = df["date"].dt.strftime("%B")
df["day"] = df["date"].dt.day


def get_season(month):
    """Returns the season based on the month."""
    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Spring"
    if month in [6, 7, 8]:
        return "Summer"
    return "Fall"


df["season"] = df["month"].apply(get_season)

text("## Filters")
weather_threshold = slider(
    "Select Weather Type (0=All, 1=Sun, 2=Rain, 3=Drizzle, 4=Snow)",
    min_val=0,
    max_val=4,
    default=0,
)

month_threshold = slider(
    "Select Month (0=All, 1=Jan, 2=Feb, 3=Mar, 4=Apr, 5=May, 6=Jun, 7=Jul, \
    8=Aug, 9=Sep, 10=Oct, 11=Nov, 12=Dec)",
    min_val=0,
    max_val=12,
    default=0,
)

weather_map = {1: "sun", 2: "rain", 3: "drizzle", 4: "snow"}
filtered_df = df.copy()

if weather_threshold != 0:
    selected_weather = weather_map.get(weather_threshold)
    filtered_df = filtered_df[filtered_df["weather"] == selected_weather]

if month_threshold != 0:
    filtered_df = filtered_df[filtered_df["month"] == month_threshold]

filtered_df["date_str"] = filtered_df["date"].dt.strftime("%Y-%m-%d")

text("*Use the sliders above to filter data by weather type and month*")

text("## Temperature Trends")

fig_temp = go.Figure()

fig_temp.add_trace(
    go.Scatter(
        x=filtered_df["date_str"],
        y=filtered_df["temp_max"],
        name="Max Temperature",
        line={"color": "firebrick", "width": 2},
        mode="lines",
    )
)

fig_temp.add_trace(
    go.Scatter(
        x=filtered_df["date_str"],
        y=filtered_df["temp_min"],
        name="Min Temperature",
        line={"color": "royalblue", "width": 2},
        mode="lines",
        fill="tonexty",
        fillcolor="rgba(0, 100, 255, 0.1)",
    )
)

fig_temp.update_layout(
    title="Daily Temperature Range",
    xaxis_title="Date",
    yaxis_title="Temperature (°C)",
    template="plotly_white",
    legend={
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "right",
        "x": 1,
    },
    margin={"l": 40, "r": 40, "t": 60, "b": 40},
    hovermode="x unified",
    xaxis={"type": "category", "categoryorder": "category ascending"},
)

plotly(fig_temp)

text("## Precipitation Analysis")
fig_precip = px.bar(
    filtered_df,
    x="date_str",
    y="precipitation",
    color="weather",
    color_discrete_map={
        "sun": "#FFD700",
        "rain": "#1E90FF",
        "drizzle": "#87CEFA",
        "snow": "#E0FFFF",
    },
    labels={"precipitation": "Precipitation (mm)", "date": "Date"},
    title="Daily Precipitation",
)

fig_precip.update_layout(
    template="plotly_white", legend_title_text="Weather Type", bargap=0.1
)

plotly(fig_precip)

text("## Weather Distribution")

weather_counts = filtered_df["weather"].value_counts().reset_index()
weather_counts.columns = ["weather", "count"]

fig_weather = px.pie(
    weather_counts,
    values="count",
    names="weather",
    hole=0.4,
    color="weather",
    color_discrete_map={
        "sun": "#FFD700",
        "rain": "#1E90FF",
        "drizzle": "#87CEFA",
        "snow": "#E0FFFF",
    },
    title="Weather Type Distribution",
)

fig_weather.update_layout(legend_title_text="Weather Type")

plotly(fig_weather)

text("## Weather Correlations")

fig_scatter = px.scatter(
    filtered_df,
    x="wind",
    y="temp_max",
    color="weather",
    color_discrete_map={
        "sun": "#FFD700",
        "rain": "#1E90FF",
        "drizzle": "#87CEFA",
        "snow": "#E0FFFF",
    },
    size="precipitation",
    hover_data=["date_str", "temp_min", "precipitation"],
    title="Correlation: Wind Speed vs Max Temperature",
    labels={"wind": "Wind Speed (mph)", "temp_max": "Maximum Temperature (°C)"},
)

fig_scatter.update_layout(template="plotly_white")

plotly(fig_scatter)

text("## Monthly Summary")

monthly_data = (
    df.groupby("month_name")
    .agg(
        {"precipitation": "sum", "temp_max": "mean", "temp_min": "mean", "wind": "mean"}
    )
    .reset_index()
)

month_order = {
    month: i
    for i, month in enumerate(
        [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
    )
}

monthly_data["month_num"] = monthly_data["month_name"].map(month_order)
monthly_data = monthly_data.sort_values("month_num")

fig_monthly = go.Figure()

fig_monthly.add_trace(
    go.Bar(
        x=monthly_data["month_name"],
        y=monthly_data["precipitation"],
        name="Total Precipitation",
        marker_color="royalblue",
        opacity=0.7,
    )
)

fig_monthly.add_trace(
    go.Scatter(
        x=monthly_data["month_name"],
        y=monthly_data["temp_max"],
        name="Avg Max Temp",
        mode="lines+markers",
        marker={"size": 10},
        line={"color": "firebrick", "width": 3},
        yaxis="y2",
    )
)

fig_monthly.add_trace(
    go.Scatter(
        x=monthly_data["month_name"],
        y=monthly_data["temp_min"],
        name="Avg Min Temp",
        mode="lines+markers",
        marker={"size": 10},
        line={"color": "darkblue", "width": 3},
        yaxis="y2",
    )
)

fig_monthly.update_layout(
    title="Monthly Weather Summary",
    xaxis={"title": "Month"},
    yaxis={"title": "Total Precipitation (mm)", "side": "left", "showgrid": False},
    yaxis2={
        "title": "Average Temperature (°C)",
        "side": "right",
        "overlaying": "y",
        "showgrid": False,
    },
    template="plotly_white",
    legend={
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "right",
        "x": 1,
    },
    margin={"l": 40, "r": 40, "t": 60, "b": 40},
)

plotly(fig_monthly)

text("## Weather Event Analysis")

monthly_weather = df.groupby(["month_name", "weather"]).size().reset_index(name="days")
monthly_weather["month_num"] = monthly_weather["month_name"].map(month_order)
monthly_weather = monthly_weather.sort_values("month_num")

fig_heatmap = px.density_heatmap(
    monthly_weather,
    x="month_name",
    y="weather",
    z="days",
    color_continuous_scale="Blues",
    title="Weather Type Frequency by Month",
)

fig_heatmap.update_layout(
    xaxis={"title": "Month"}, yaxis={"title": "Weather Type"}, template="plotly_white"
)

plotly(fig_heatmap)

text("## Precipitation Patterns")

df["has_precip"] = df["precipitation"] > 0
df["streak_start"] = (df["has_precip"] != df["has_precip"].shift(1)) & df["has_precip"]
df["streak_group"] = df["streak_start"].cumsum()

streaks = df[df["has_precip"]].groupby("streak_group").size().reset_index(name="days")
max_streak = streaks["days"].max()

wettest_day = df.loc[df["precipitation"].idxmax()]

precip_stats = pd.DataFrame(
    {
        "Metric": [
            "Total Annual Precipitation (mm)",
            "Longest Streak of Rainy Days",
            "Wettest Day",
            "Wettest Day Precipitation (mm)",
            "Days with Precipitation",
            "Days with Snow",
        ],
        "Value": [
            round(df["precipitation"].sum(), 1),
            max_streak,
            wettest_day["date"].strftime("%Y-%m-%d"),
            wettest_day["precipitation"],
            df[df["precipitation"] > 0].shape[0],
            df[df["weather"] == "snow"].shape[0],
        ],
    }
)

table(precip_stats, title="Precipitation Statistics")

text("## Wind Analysis")

fig_wind = px.histogram(
    df,
    x="wind",
    color="weather",
    color_discrete_map={
        "sun": "#FFD700",
        "rain": "#1E90FF",
        "drizzle": "#87CEFA",
        "snow": "#E0FFFF",
    },
    nbins=20,
    title="Wind Speed Distribution",
    labels={"wind": "Wind Speed (mph)", "count": "Number of Days"},
)

fig_wind.update_layout(
    xaxis_title="Wind Speed (mph)",
    yaxis_title="Number of Days",
    template="plotly_white",
    bargap=0.1,
)

plotly(fig_wind)
