from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

text("# PRESWALD Take HOME Assignment")
text("Welcome to my Phone Comparison Project")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')


sql = """
    SELECT "Company Name" AS Brand, 
           "Model Name" AS Model, 
           CAST(REGEXP_REPLACE("Launched Price (USA)", '[^0-9.]', '', 'g') AS NUMERIC) AS "Price (USA)", 
           ROUND(CAST(REGEXP_REPLACE("Launched Price (India)", '[^0-9.]', '', 'g') AS NUMERIC) / 83, 1) AS "Price (India in USD)", 
           ROUND(CAST(REGEXP_REPLACE("Launched Price (China)", '[^0-9.]', '', 'g') AS NUMERIC) / 7.2, 1) AS "Price (China in USD)",
           ROUND(CAST(REGEXP_REPLACE("Launched Price (Dubai)", '[^0-9.]', '', 'g') AS NUMERIC) / 3.67, 1) AS "Price (Dubai in USD)"
    FROM sample_csv
"""


filtered_df = query(sql, "sample_csv")
table(filtered_df, title="Filtered Data")



#Threshold to filter price by every country - 

#USAAAAAAAAAAAA

threshold_usa = slider("Threshold for USA Price ( USD )", min_val=0, max_val=2000, default=800)
usa_filtered_data = filtered_df[filtered_df["Price (USA)"] > threshold_usa]
text("### USA Price Threshold Filtered Data")
table(usa_filtered_data, title=f"USA Price Threshold: {threshold_usa} USD")


#INDIAAAAAA

threshold_india = slider("Threshold for India Price ( USD )", min_val=0, max_val=2000, default=800)
india_filtered_data = filtered_df[filtered_df["Price (India in USD)"] > threshold_india]

text("### India Price Threshold Filtered Data")
table(india_filtered_data, title=f"India Price Threshold: {threshold_india} USD")


#Chinaa
threshold_china = slider("Threshold for China Price ( USD )", min_val=0, max_val=2000, default=800)
china_filtered_data = filtered_df[filtered_df["Price (China in USD)"] > threshold_china]
text("### China Price Threshold Filtered Data")
table(china_filtered_data, title=f"China Price Threshold: {threshold_china} USD")


#Dubaiii
threshold_dubai = slider("Threshold for Dubai Price ( USD )", min_val=0, max_val=2000, default=800)
dubai_filtered_data = filtered_df[filtered_df["Price (Dubai in USD)"] > threshold_dubai]

text("### Dubai Price Threshold Filtered Data")
table(dubai_filtered_data, title=f"Dubai Price Threshold: {threshold_dubai} USD")




#PLOTTING TIME!!

# THESE PLOTS Compare - USA VS INDIA , USA VS CHINA AND USA VS DUBAI PRICES

# Scatter plot comparing USA vs India
fig1 = px.scatter(
    filtered_df,
    x="Price (USA)", 
    y="Price (India in USD)", 
    color="Model",  # Color by model for distinction
    title="Price Comparison: USA vs India",
    labels={
        "Price (USA)": "Price in USA (USD)", 
        "Price (India in USD)": "Price in India (USD)"
    },
    hover_data=["Model", "Brand"]
)

# Scatter plot comparing USA vs China
fig2 = px.scatter(
    filtered_df,
    x="Price (USA)", 
    y="Price (China in USD)", 
    color="Model",  # Color by model for distinction
    title="Price Comparison: USA vs China",
    labels={
        "Price (USA)": "Price in USA (USD)", 
        "Price (China in USD)": "Price in China (USD)"
    },
    hover_data=["Model", "Brand"]
)

# Scatter plot comparing USA vs Dubai
fig3 = px.scatter(
    filtered_df,
    x="Price (USA)", 
    y="Price (Dubai in USD)", 
    color="Model",  # Color by model for distinction
    title="Price Comparison: USA vs Dubai",
    labels={
        "Price (USA)": "Price in USA (USD)", 
        "Price (Dubai in USD)": "Price in Dubai (USD)"
    },
    hover_data=["Model", "Brand"]
)

plotly(fig1)
plotly(fig2)
plotly(fig3)