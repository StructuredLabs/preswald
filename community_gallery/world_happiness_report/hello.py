from preswald import connect, get_df, text, table, plotly, selectbox
import plotly.express as px
import pandas as pd

connect()
df = get_df("happiness_2023")

text("# World Happiness Explorer")
text("Uncover the Secrets of Global Happiness (2023 Data)")

country = selectbox("Select Country", options=df["Country name"].unique().tolist(), default="United States")
selected_year = 2023

filtered_df = df[df["Country name"] == country]

text("## Happiness Overview")
text(f"Happiness score for {country} in {selected_year}.")
fig_map = px.choropleth(
    filtered_df,
    locations="Country name",
    locationmode="country names",
    color="Ladder score",
    hover_name="Country name",
    title=f"Happiness Score in {country} (2023)",
    color_continuous_scale="Viridis",
    height=500
)
fig_map.update_layout(title_x=0.5, title_font_size=20)
plotly(fig_map)

text("## Happiness Details")
text(f"Key metrics for {country} in {selected_year}.")
details_df = filtered_df[["Country name", "Ladder score", "Logged GDP per capita", "Social support", "Healthy life expectancy"]]
table(details_df, title=f"Happiness Metrics for {country} (2023)")

text("## Exploring Happiness Factors")
text(f"Analyze happiness factors for {country} in {selected_year}.")
fig_gdp = px.scatter(
    filtered_df,
    x="Logged GDP per capita",
    y="Ladder score",
    hover_data=["Country name"],
    title=f"Happiness vs GDP per Capita in {country} (2023)",
    labels={"Ladder score": "Happiness Score"},
    color="Social support",
    size="Healthy life expectancy",
    height=500
)
fig_gdp.update_layout(title_x=0.5, title_font_size=20)
plotly(fig_gdp)

text("## Summary Statistics")
text(f"Stats for {country} in {selected_year}.")
stats_df = pd.DataFrame({
    "Metric": ["Happiness Score", "GDP per Capita", "Social Support", "Healthy Life Expectancy"],
    "Value": [
        filtered_df["Ladder score"].iloc[0] if not filtered_df.empty else "N/A",
        filtered_df["Logged GDP per capita"].iloc[0] if not filtered_df.empty else "N/A",
        filtered_df["Social support"].iloc[0] if not filtered_df.empty else "N/A",
        filtered_df["Healthy life expectancy"].iloc[0] if not filtered_df.empty else "N/A"
    ]
}).round(2)
table(stats_df, title=f"Summary Stats for {country} (2023)")

text("---")
text("Data source: [World Happiness Report 2023](https://www.kaggle.com/datasets/ajaypalsinghlo/world-happiness-report-2023)")