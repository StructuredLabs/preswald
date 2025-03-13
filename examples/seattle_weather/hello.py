from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px

connect()  # Initialize connection to preswald.toml data sources
df = get_df("seattleWeather_csv")  # Load data

sql = "SELECT * FROM seattleWeather_csv WHERE weather = 'sun'"
filtered_df = query(sql, "seattleWeather_csv")
 
text("# Weather Prediction Data Analysis App")
table(filtered_df, title="Filtered Data")

threshold = slider("Temperature Threshold", min_val=0, max_val=50, default=25)
table(df[df["temp_max"] > threshold], title="Days with High Temperatures")

fig = px.scatter(df, x="wind", y="temp_max", color="weather", title="Wind Speed vs Max Temperature")
plotly(fig)