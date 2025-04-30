from preswald import text, plotly, connect, get_df, table, query, slider, selectbox
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('global_energy_consumption')

if df is None or df.empty:
    text("Data could not be loaded! Check preswald.toml once")
    print("Data could not be loaded! Check preswald.toml once")
    exit()

selected_year = slider("Select Year", min_val=2000, max_val = 2024, default = 2024)
selected_year = int(selected_year)



sql = f"Select * from global_energy_consumption WHERE Year = {selected_year}"
filtered_df = query(sql, "global_energy_consumption")

table(filtered_df, title=f"Energy data for {selected_year}")

# Create a scatter plot
fig = px.scatter(filtered_df, 
                 x="Country", 
                 y="Total Energy Consumption (TWh)",
                 color="Country",
                 title="Total Energy Consumption Over the Years by Country",
                 labels={"Total Energy Consumption (TWh)": "Energy Consumption (TWh)", 
                         "Year": "Year",
                         "Carbon Emissions (Million Tons)":"Carbon Emissions"})

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# Style the plot
fig.update_layout(template='plotly_white')

# Show the plot
plotly(fig)

# Show the data

