from preswald import text, plotly, connect, get_df, table, slider, separator, text_input, selectbox
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

text("# A dashboard to visualize mobile data till 2025")

# Load the CSV
# connect() # load in all sources, which by default is the sample_csv
# df = get_df('data/mobiles_data_2025.csv')
df = pd.read_csv("data/mobiles_data_2025.csv")

separator()

text("# Top 10 Brands By Number of Models")
# Get the top 10 brands by number of models
top_10_brands = df["Company Name"].value_counts().head(10)

# Create an interactive bar chart with Plotly
fig_top_ten = px.bar(
    x=top_10_brands.values,
    y=top_10_brands.index,
    orientation='h',
    title="Top 10 Brands by Number of Models",
    labels={"x": "Number of Models", "y": "Brand"},
    color=top_10_brands.values,
    color_continuous_scale="viridis"
)

# Add labels for each point
# fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# Style the plot
fig_top_ten.update_layout(template='plotly_white')

# Show the plot
plotly(fig_top_ten)


separator()

text("# Brand Market Share")
# Get brand market share (percentage of total models)
brand_market_share = df["Company Name"].value_counts(normalize=True) * 100

# Create an interactive pie chart
fig_market_share = px.pie(
    names=brand_market_share.index,
    values=brand_market_share.values,
    title="Market Share of Each Brand (Based on Number of Models)",
    color_discrete_sequence=px.colors.sequential.Viridis
)

plotly(fig_market_share)


separator()

text("# Number of Models Launched Yearly")
# Count the number of models launched each year
models_per_year = df["Launched Year"].value_counts().sort_index()

# Create an interactive line chart
fig_models_per_year = px.line(
    x=models_per_year.index,
    y=models_per_year.values,
    markers=True,
    title="Number of Models Launched Per Year",
    labels={"x": "Year", "y": "Number of Models"}
)

plotly(fig_models_per_year)

separator()

# Function to clean and safely convert prices
def clean_price(price):
    if pd.isna(price) or not isinstance(price, str):  # Handle NaN and non-string values
        return np.nan  # Return NaN if empty or invalid
    
    price_str = "".join(filter(str.isdigit, str(price)))  # Remove non-numeric characters
    return float(price_str) if price_str else np.nan  # Convert or return NaN if empty

text("# Dyanmic Price Vs Battery Comparison for Phone Models")

selected_battery_capacity = slider("Select Battery Capacity",min_val=2000, max_val=10000, default=3000)
# Ensure Battery Capacity and Prices are numeric and handle missing values

df1 = df.copy()

# Clean Battery Capacity Column
df1["Battery Capacity"] = df1["Battery Capacity"].str.replace(",", "").str.replace("mAh", "").astype(float)

df1["Launched Price (USA)"] = df1["Launched Price (USA)"].apply(clean_price)

# Filter dataset for phones with Battery Capacity ≤ selected value
filtered_df = df1[df1["Battery Capacity"] <= selected_battery_capacity]

# Ensure we have data to process
if filtered_df.empty:
    print(f"No data available for Battery Capacity ≤ {selected_battery_capacity}mAh.")
else:
    # Group data by brand and compute the average price for these battery capacities
    avg_price_brand_battery = filtered_df.groupby("Company Name")["Launched Price (USA)"].mean().reset_index()

    # Create a grouped bar chart for price comparison across brands
    fig = px.bar(
        avg_price_brand_battery, 
        x="Company Name", 
        y="Launched Price (USA)", 
        color="Company Name",
        title=f"Price Comparison by Brand for Battery Capacity ≤ {selected_battery_capacity}mAh",
        labels={"Company Name": "Brand", "Launched Price (USA)": "Avg Price (USD)"}
    )

    plotly(fig)

separator()

text("# Average Launch Price of Phones Based On Selected Region")

list_launched_price_col = [col for col in df.columns if "Launched Price" in col] 

# Convert user input to the corresponding column name
selected_column =  selectbox(label="Choose a Launch Price Region",options=list_launched_price_col) # Default to USA if input is invalid

df[selected_column] = df[selected_column].apply(clean_price) # cleaning the price data for selected column

# Filter data based on selected region
region_price_data = df.groupby("Company Name")[selected_column].mean().sort_values(ascending=False)

# Create interactive bar chart
fig_launch_price_region = go.Figure()

fig_launch_price_region.add_trace(go.Bar(
    x=region_price_data.values,
    y=region_price_data.index,
    orientation='h',
    marker=dict(color=region_price_data.values, colorscale="viridis"),
    name=f"Average Price in {selected_column}"
))

fig_launch_price_region.update_layout(
    title=f"Average Phone Price in {selected_column}",
    xaxis_title="Average Price",
    yaxis_title="Brand"
)

plotly(fig_launch_price_region)

separator()

text("# Search Phone Prices")

search_query = text_input(label="Enter your Phone Name", placeholder="iPhone")  # Example: User searches for "iPhone"

# Filter data where the Model Name or Company Name contains the search term
filtered_df = df[df["Model Name"].str.contains(search_query, case=False, na=False) |
                 df["Company Name"].str.contains(search_query, case=False, na=False)]

# Create a bar chart showing the price of searched models
fig_search_query = px.bar(
    filtered_df,
    x="Model Name",
    y="Launched Price (USA)",
    color="Company Name",
    title=f"Search Results for '{search_query}'",
    labels={"Launched Price (USA)": "Price (USD)"},
    text_auto=True
)

plotly(fig_search_query)

# Display the full dataset
text("## Full Dataset")
text("Below is the full dataset used for this analysis.")
table(df)
