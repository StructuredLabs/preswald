from preswald import connect, get_df, table, text, selectbox, slider, plotly
import plotly.express as px

# 🌎 **Multi-City Weather Comparison Dashboard**
text("# Multi-City Weather Comparison Dashboard")
connect()  # Initialize data source connection
df = get_df("multi_city_weather")  # Load dataset

if df is None or df.empty:
    text("Error: Dataset could not be loaded. Check `preswald.toml`.")
else:
    text("Dataset loaded successfully!")

    # **Searchable City Selection with Filtering**
    city_options = sorted(df["City"].unique().tolist())  # Sort for better UI
    city_1 = selectbox("🔍 Select City 1 (Type to Search)", city_options, size=0.5)
    city_2 = selectbox("🔍 Select City 2 (Type to Search)", city_options, size=0.5)

    if city_1 and city_2:
        # **Slider to filter temperature threshold**
        temp_threshold = slider("🌡 Set Temperature Threshold (°C)", 
                                min_val=int(df["Temperature Avg"].min()), 
                                max_val=int(df["Temperature Avg"].max()), 
                                default=int(df["Temperature Avg"].mean()))

        # **Filter Data for Selected Cities**
        filtered_df = df[(df["City"].isin([city_1, city_2])) & (df["Temperature Avg"] > temp_threshold)]

        if filtered_df.empty:
            text(f"⚠️ No data available for {city_1} & {city_2} above {temp_threshold}°C.")
        else:
            # **Relevant Columns Only**
            selected_columns = ["Date", "City", "Temperature Avg", "Temperature Max", 
                                "Temperature Min", "Humidity Avg", "Wind Speed Avg", "Precipitation"]
            table(filtered_df[selected_columns], title=f"📊 Weather Data for {city_1} vs {city_2}")

            # **Graph Enhancements**
            text("## 📈 Weather Comparison Between Cities")

            # 🌡️ **Temperature Comparison**
            fig1 = px.bar(filtered_df, x="City", y=["Temperature Max", "Temperature Avg", "Temperature Min"], 
                          barmode="group", title="🌡️ Temperature Comparison",
                          labels={"value": "Temperature (°C)", "City": "Selected Cities"},
                          color_discrete_sequence=["#FF5733", "#33FF57", "#337BFF"])
            plotly(fig1)

            # 💦 **Humidity Comparison**
            fig2 = px.scatter(filtered_df, x="City", y="Humidity Avg", color="City",
                              title="💧 Humidity Levels",
                              labels={"Humidity Avg": "Humidity (%)", "City": "Selected Cities"},
                              size="Humidity Avg", template="plotly_dark")
            plotly(fig2)

            # 💨 **Wind Speed Comparison**
            fig3 = px.line(filtered_df, x="City", y="Wind Speed Avg", color="City",
                           title="💨 Wind Speed Comparison",
                           labels={"Wind Speed Avg": "Wind Speed (km/h)", "City": "Selected Cities"},
                           line_shape="spline", template="simple_white")
            plotly(fig3)

            # 🌧 **Precipitation Comparison**
            fig4 = px.bar(filtered_df, x="City", y="Precipitation", color="City",
                          title="🌧 Precipitation Levels",
                          labels={"Precipitation": "Precipitation (mm)", "City": "Selected Cities"},
                          color_discrete_map={city_1: "blue", city_2: "green"}, text_auto=True)
            plotly(fig4)

            # 🌍 **City Weather Variation**
            fig5 = px.scatter(filtered_df, x="Temperature Avg", y="Humidity Avg", color="City",
                              size="Wind Speed Avg", hover_data=["Precipitation"],
                              title="🌍 City Weather Variation",
                              labels={"Temperature Avg": "Temperature (°C)", "Humidity Avg": "Humidity (%)"},
                              template="seaborn")
            plotly(fig5)

        # **Dynamic Data View (Filtered)**
        text("## 🔄 Dynamic Weather Data Filtering")
        table(df[df["Temperature Avg"] > temp_threshold][selected_columns], 
              title=f"Filtered Data (Temp > {temp_threshold}°C)")
