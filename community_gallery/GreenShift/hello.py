from preswald import text, plotly, connect, get_df, table
import preswald as ps
import pandas as pd
import plotly.express as px

# Project Title
text("# GreenShift: Renewable Energy Adoption and Carbon Footprint Analysis")


# Load the CSV
ps.connect() # load in all sources, which by default is the sample_csv
#df = get_df('sample_csv') 
# Load datasets
#renewable_df = get_df('renewable_energy')
#co2_df = get_df('co2_emissions')

# Data Preprocessing
# Load Renewable Energy Data
renewable_df = pd.read_csv("data/modern-renewable-prod.csv")

# Load CO₂ Emissions Data
co2_df = pd.read_csv("data/annual-co2-emissions-per-country.csv")

# Display first few rows
print("Renewable Energy Data:")
print(renewable_df.head())

print("\nCO₂ Emissions Data:")
print(co2_df.head())

print("Missing values in Renewable Energy Data:\n", renewable_df.isnull().sum())
print("\nMissing values in CO₂ Emissions Data:\n", co2_df.isnull().sum())

renewable_df.fillna(0, inplace=True)  # Fill missing renewable energy values with 0
co2_df.ffill(inplace=True)  # Forward-fill missing CO2 emissions


# Rename columns for uniformity
renewable_df.rename(columns={'Entity': 'Country', 'Code': 'Country_Code', 'Year': 'Year'}, inplace=True)
co2_df.rename(columns={'Entity': 'Country', 'Code': 'Country_Code', 'Year': 'Year', 'Annual CO₂ emissions': 'CO2_Emissions_Tonnes'}, inplace=True)

# Convert CO2 emissions to million tonnes
co2_df['CO2_Emissions_Million_Tonnes'] = co2_df['CO2_Emissions_Tonnes'] / 1e6

# Merge datasets on 'Entity' and 'Year'
merged_df = pd.merge(renewable_df, co2_df[['Country', 'Year', 'CO2_Emissions_Million_Tonnes']], on=['Country', 'Year'], how='inner')

merged_df.drop_duplicates(inplace=True)

# Save cleaned dataset
merged_data_path = "data/cleaned_energy_co2.csv"
merged_df.to_csv(merged_data_path, index=False)

df = pd.read_csv(merged_data_path)

# Define initially visible countries
initial_countries = ["United States", "India", "China", "Germany"]

# Create an interactive scatter plot
fig = px.line(df, x='Year', y='CO2_Emissions_Million_Tonnes', 
                 color='Country', 
                 title='CO₂ Emissions Over Time',
                 labels={'Year': 'Year', 'CO2_Emissions_Million_Tonnes': 'CO₂ Emissions (Million Tonnes)'})

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# Update traces: Show only selected countries, hide others
for trace in fig.data:
    trace.visible = "legendonly" if trace.name not in initial_countries else True


# Style the plot
fig.update_layout(template='plotly_white')

# Show the plot
plotly(fig)

# Filter the dataframe to show only selected countries
filtered_df = df[df["Country"].isin(initial_countries)]

# Display the filtered table
table(filtered_df)

#api key = prswld-b8c56d7e-2b80-468e-905d-1919873c068e
#i Custom domain assigned at greenshift-660129-inh5wcbv.preswald.app
#i App is available here https://greenshift-660129-inh5wcbv-ndjz2ws6la-ue.a.run.app
#i Custom domain assigned at greenshift-660129-inh5wcbv.preswald.app
#preswald deploy --target structured --github kunalmore984 --api-key prswld-b8c56d7e-2b80-468e-905d-1919873c068e hello.py
