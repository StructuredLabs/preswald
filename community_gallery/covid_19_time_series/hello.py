from preswald import text, plotly, table, slider, connect, get_df
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO
import os

# Function to download CSV files from google drive
def download_csv_from_googledrive(file_id, filepath):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(filepath, "w") as f:
            f.write(response.text)
        return pd.read_csv(StringIO(response.text))
    else:
        raise Exception(f"Failed to download file from {url}")

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Connect to Preswald
connect()

# Check if CSV files exist; if not, download them from google drive and save them
if not os.path.exists("data/time_series_covid19_confirmed_US.csv"):
    df_cases = download_csv_from_googledrive("1QXoAHPMDhEYNbSh4IO_w3EyhHJ_oAad1", "data/time_series_covid19_confirmed_US.csv")
else:
    df_cases = get_df("time_series_covid19_confirmed_US")

if not os.path.exists("data/time_series_covid19_deaths_US.csv"):
    df_deaths = download_csv_from_googledrive("1tFmQOpsrrDOdCSbrEkAtcDhRBZ--V3Js", "data/time_series_covid19_deaths_US.csv")
else:
    df_deaths = get_df("time_series_covid19_deaths_US")

# The dated data starts from column 11 and onwards. Select them from the CSV
date_cols = df_cases.columns[11:]
date_cols_deaths = df_deaths.columns[11:]

# Create a date slider so the user can see the COVID situation for a specific date
date_index = slider("Select Date (Days since January 22, 2020)", min_val=0, max_val=len(date_cols)-1, default=400, step=1, size=0.5)
selected_date = date_cols[date_index]

# Assign selected date values
df_cases["Cases"] = df_cases[selected_date]
df_cases["text"] = df_cases["Combined_Key"] + "<br>Cases: " + df_cases["Cases"].astype(str)

df_deaths["Deaths"] = df_deaths[selected_date]
df_deaths["text"] = df_deaths["Combined_Key"] + "<br>Deaths: " + df_deaths["Deaths"].astype(str)

# Define color scale and limit breakpoints
limits_cases = [(0, 1000), (1000, 10000), (10000, 20000), (20000, 50000), (50000, df_cases["Cases"].max() + 1)]
limits_deaths = [(0, 50), (50, 200), (200, 400), (400, 800), (800, 1500), (1500, df_deaths["Deaths"].max() + 1)]
colors = ["grey", "#edd072", "#e6a455", "#d46833", "#d1371f", "#800101"]

# Make the bubble map
def generate_bubble_map(df, value_col, limits, title, size_factor=500):
    fig = go.Figure()
    for i, (low, high) in enumerate(limits):
        df_sub = df[(df[value_col] >= low) & (df[value_col] < high)]
        if not df_sub.empty:
            fig.add_trace(go.Scattergeo(
                locationmode="USA-states",
                lon=df_sub["Long_"],
                lat=df_sub["Lat"],
                text=df_sub["text"],
                marker=dict(
                    size=df_sub[value_col].clip(lower=10) / size_factor,
                    color=colors[i],
                    line_color="black",
                    line_width=0.5,
                    sizemode="area"
                ),
                name=f"{low} - {high} {value_col}"
            ))
    fig.update_layout(
        title_text=title,
        geo=dict(scope="usa", landcolor="rgb(217,217,217)"),
        template="plotly_white"
    )
    return fig

# Generate the confirmed case and deaths bubble maps using the function defined above
fig_cases = generate_bubble_map(df_cases, "Cases", limits_cases, f'US COVID-19 Confirmed Cases on {selected_date}', size_factor=500)
fig_deaths = generate_bubble_map(df_deaths, "Deaths", limits_deaths, f'US COVID-19 Confirmed Deaths on {selected_date}', size_factor=50)

# Merge datasets for a combined data table that will go below the bubble maps
merged_df = pd.merge(
    df_cases[["Combined_Key", selected_date]].rename(columns={selected_date: "Confirmed Cases"}),
    df_deaths[["Combined_Key", selected_date]].rename(columns={selected_date: "Confirmed Deaths"}),
    on="Combined_Key"
)

# Display results
text(f"# US COVID-19 Cumulative Confirmed Cases on {selected_date}")
plotly(fig_cases)

text(f"# US COVID-19 Cumulative Confirmed Deaths on {selected_date}")
plotly(fig_deaths)

# Show the combined table
table(merged_df, title=f"Cumulative Confirmed Cases & Deaths by county on {selected_date}")
