from preswald import text, plotly, connect, get_df, table, query, separator, slider, checkbox
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go




# Load the dataset
SOURCE_NAME = "amzn_csv"
connect() # load in sources
df = get_df(SOURCE_NAME)



# Build UI

# Title/Info
text("## AMZN Stock Magic ✨ (Preswald Project by [Anantjyot Grang](https://www.linkedin.com/in/anantjyot-grang/))")
text("As a stock enthusiast and investor, what better way to build my first Preswald project than by analyzing my favorite company—Amazon! Let's use Preswald to explore trends and insights in the AMZN stock.")
separator()



# Minimum year selector
text("## Configure")
text("First set the minimum year you want below. The dataset spans from 1977 - 2025.")
min_year = slider(
    label="Data Range Lower Bound",
    min_val=1977,
    max_val=2024,
    step=1,
    default=1977
)
text(f"Selected: {min_year}")
df = df[df["Date"].dt.year >= min_year] # Filter dataset based on selected minimum year
df["Date"] = df["Date"].astype(str) # Convert Date to string to avoid JSON serialization issue in Plotly
separator()


# Create a line graph for the AMZN stock price, allowing user to select which price factors to view
text("## Stock Price Over Time")
close_price = checkbox(label="Closing Price", size=0.25, default=True)
open_price = checkbox(label="Opening Price", size=0.25)
low_price = checkbox(label="Day's Low", size=0.25)
high_price = checkbox(label="Day's High", size=0.25)

y_axes = [] # Determine y-axes to display based on checkbox selection
if (close_price): y_axes.append("Close")
if (open_price): y_axes.append("Open")
if (low_price): y_axes.append("Low")
if (high_price): y_axes.append("High")


if (len(y_axes) > 0): 
    price_fig = px.line(df, x="Date", y=y_axes, title="Price (USD) VS Date")
    price_fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue')) # Add labels for each point
    price_fig.update_layout(template='plotly_white') # Style the plot
    plotly(price_fig) # Show the plot

else: # If no price factor selected, display default message
    text("Select a price option to display")
separator()


# Volume bar chart
text("## Volume")
vol_fig = px.bar(df, x="Date", y="Volume", title="AMZN Trading Volume VS Date")
plotly(vol_fig)
separator()


# Stock split history scatter plot
text("## Stock Split History")
sql = f"""SELECT * FROM {SOURCE_NAME} WHERE "Stock Splits" > 0""" # Determine data points for which a stock split exists
filtered_df = query(sql, SOURCE_NAME) # Apply SQL query and get filtered df
filtered_df["Date"] = filtered_df["Date"].astype(str) # Convert Date to string to avoid JSON serialization issue in Plotly

split_fig = px.scatter( # Display scattter plot
    filtered_df, x="Date", y="Stock Splits", text="Stock Splits",
    title="Split Ratio VS Date",
    labels={"Stock Splits": "Split Ratio"}
)

split_fig.update_traces(marker=dict(size=10, color="red"), textposition="top center") # Update scatter plot styling
plotly(split_fig)
separator()



# Table of data
text("## Dataset Viewer")
table(df.round(2), title=None) # Show all the data in table form (cleaned, rounded to 2 decimals)

