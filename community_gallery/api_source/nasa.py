from preswald.interfaces.components import text, table, plotly, image, alert, progress, selectbox, slider, checkbox, button, spinner, separator
from preswald.interfaces.data import connect, get_df
import pandas as pd
import plotly.express as px

connect()

# Fetch data from the NASA APOD API
df_apod = get_df('nasa_apod')

text("# NASA Astronomy Picture of the Day (APOD)")
text("Explore the cosmos! 🚀")

if not df_apod.empty:
    text("### Today's APOD Data")
    table(df_apod)

    if 'url' in df_apod.columns:
        text("### APOD Image")
        image(df_apod['url'].iloc[0], alt="Astronomy Picture of the Day")
    else:
        alert("⚠️ No image URL found in the APOD data.", level="warning")

    if 'explanation' in df_apod.columns:
        text("### Explanation")
        text(df_apod['explanation'].iloc[0])
    else:
        alert("No explanation found in the APOD data.", level="warning")
        
else:
    alert("⚠️ No data returned from the NASA APOD API.", level="error")