from preswald import alert, text, plotly, connect, get_df, table, query, selectbox, slider
import pandas as pd
import plotly.express as px

text("# Global Sustainable Energy Investigation 🌎\n Welcome to the **Global Sustainable Energy Investigation**, an interactive platform designed to explore the world’s \
      progress toward sustainable electricity access. Use it to: \
      \n1. Track Global Energy Trends: Use the slider to change the year and select an electricity source to see how \
        its global usage has evolved over time. \
      \n2. Electricity Access: Select a country to visualize the percentage of its population with electricity access over the years. \
        To access the dataset, \
        checkout [this](https://www.kaggle.com/datasets/anshtanwar/global-data-on-sustainable-energy) Kaggle dataset")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('globalDataEnergy')

#TASK 1
alert(message="Use the slider to change the year and select an electricity source \
                to see how its global usage has evolved over time.", 
        level="info")

#select year and electricty source
year_input = slider( 
        label="Slide to Choose Year",
        min_val= 2000,
        max_val= 2020,
        step= 1.0
    ) 
electricity_source_input = selectbox(
        label="Choose Electricity Source",
        options=["fossil fuels", "nuclear", "renewables"]
    )

#query year and source
sql = f"""
            SELECT Entity, "Electricity from {electricity_source_input} (TWh)"
            FROM globalDataEnergy 
            WHERE Year = {year_input}  
        """
electricity_source = query(sql, "globalDataEnergy")

#create a geo map using input
color_scale = "Reds"
if electricity_source_input == "renewables":
    color_scale = "Greens"
   

fig = px.choropleth(electricity_source, locations="Entity", locationmode="country names",
                    color=f"Electricity from {electricity_source_input} (TWh)",
                    color_continuous_scale=color_scale, 
                    range_color=[0, 3000] 
                )

plotly(fig)

#TASK 2
alert(message="Select a country to see the percentage of the population \
               with access to electricity over time.", 
        level="info")

#select country to analyze access to electricity 
country_input = selectbox(
        label="Choose Country",
        options=df["Entity"].unique().tolist()
    )

#query data
sql = f"""
        SELECT *
        FROM globalDataEnergy 
        WHERE Entity = '{country_input}'
    """
us_electricity_access = query(sql, "globalDataEnergy")

# Create scatter plot
fig = px.scatter(us_electricity_access, x="Year", 
        y="Access to electricity (% of population)", 
        title=f"{country_input}'s Percent of Population with Access to Electricity from 2000 to 2020"
    )

# Update layout
fig.update_layout(
    template='plotly_white',
    xaxis_title="Year", 
    yaxis_title="Access to Electricity (%)"  
)

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# Show the plot
plotly(fig)

# Show the data
table(us_electricity_access, title= f"{country_input}'s Energy and Economic Data from 2000-2020")
