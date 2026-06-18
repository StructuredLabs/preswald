import numpy as np
import pandas as pd
import plotly.express as px
from preswald import text, plotly, connect, get_df, table, slider, selectbox

text("# Weather Dashboard🌤️")


connect()
df = get_df("seattleWeather_csv")

if df is None or df.empty:
    text("⚠️ **Error:** Dataset 'seattleWeather_csv' not found! Check `preswald.toml`.")
else:
    
    if "date" in df.columns:
        df["date"] = df["date"].astype(str)

    text("### Select Weather Condition")
    weather_condition = selectbox("Choose Weather Type☁️", 
                                  ["All", "rain", "sun", "snow", "drizzle"], 
                                  default="All")

    temp_threshold = slider("Minimum Temperature (°C)🌡️", 
                            min_val=int(df["temp_min"].min()), 
                            max_val=int(df["temp_max"].max()), 
                            default=int(df["temp_min"].mean()))

    text("### 📊 Choose Chart Type")
    chart_type = selectbox("Select Chart Type", 
                           ["Line Chart", "Bar Chart", "Scatter Plot"], 
                           default="Line Chart")

 
    df_filtered = df[df["temp_min"] >= temp_threshold]
    if weather_condition != "All":
        df_filtered = df_filtered[df_filtered["weather"].str.lower() == weather_condition.lower()]

 
    df_filtered = df_filtered.copy()
    float_columns = ["temp_max", "temp_min"]
    df_filtered[float_columns] = df_filtered[float_columns].astype(np.float64)

    
    fig = None
    if not df_filtered.empty:
        if chart_type == "Line Chart":
            fig = px.line(df_filtered, x="date", y=["temp_max", "temp_min"], 
                          title=f"Seattle Temperature Trends ({weather_condition})",
                          labels={"date": "Date", "value": "Temperature (°C)"},
                          template="plotly_dark")
        elif chart_type == "Bar Chart":
            fig = px.bar(df_filtered, x="date", y="temp_max", color="temp_max",
                         title=f"Max Temperatures Over Time ({weather_condition})",
                         labels={"date": "Date", "temp_max": "Max Temperature (°C)"},
                         template="plotly_dark")
        elif chart_type == "Scatter Plot":
            fig = px.scatter(df_filtered, x="date", y="temp_max", color="temp_max",
                             title=f"Temperature Scatter Plot ({weather_condition})",
                             labels={"date": "Date", "temp_max": "Max Temperature (°C)"},
                             template="plotly_dark")

        plotly(fig)

    table(df_filtered, title="Filtered Weather Data:")
