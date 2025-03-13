from preswald import connect, get_df, plotly, separator, text
import pandas as pd
import plotly.express as px

connect()

data = get_df("air_quality")

data['Start_Date'] = pd.to_datetime(data['Start_Date'], format='%m/%d/%Y', errors='coerce')
data['Start_Date'] = data['Start_Date'].dt.strftime("%Y-%m-%d")

ozone_df = data[data['Name'] == 'Ozone (O3)']

text("## New York City Air Quality Surveillance Data")

scatter_fig = px.scatter(
    ozone_df,
    x='Start_Date',
    y='Data Value',
    title='Scatter Plot: Ozone (O3) Levels Over Time',
    labels={'Start_Date': 'Start Date', 'Data Value': 'Data Value (ppb)'},
    opacity=0.7,
    color_discrete_sequence=['red']
)

separator()
histogram_fig = px.histogram(
    ozone_df,
    x='Data Value',
    nbins=20,
    title='Histogram of Ozone (O3) Measurements',
    labels={'Data Value': 'Ozone (O3) Data Value (ppb)'},
    color_discrete_sequence=['green']
)
histogram_fig.update_layout(
    template='plotly_white',
    xaxis_title='Ozone (O3) Data Value (ppb)',
    yaxis_title='Frequency',
)

text("This scatter plot illustrates how the Ozone (O3) measurements vary over time, highlighting trends and fluctuations, as well as identifying any anomalies in the data.")
plotly(scatter_fig)


text("The histogram displays the distribution of ozone levels across the measurements, showing the frequency of different concentration ranges and helping to identify the central tendency and spread.")
plotly(histogram_fig)