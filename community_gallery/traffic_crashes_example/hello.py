
import pandas as pd
import plotly.express as px
from preswald import connect, table, text, plotly, slider

connect()

data_file = "data/Traffic.csv"

df = pd.read_csv("data/Traffic.csv")

if df is not None:
    text("Data loaded successfully!")

    df = df.dropna(subset=['LATITUDE', 'LONGITUDE', 'INJURIES_TOTAL', 'CRASH_TYPE'])

    fig = px.scatter(df, x="LATITUDE", y="LONGITUDE", color="CRASH_TYPE", title="Traffic Crashes by Location and Crash Type")
    plotly(fig)

    severity_counts = df['INJURIES_TOTAL'].value_counts().reset_index()
    severity_counts.columns = ['Injuries', 'Count']
    fig2 = px.bar(severity_counts, x='Injuries', y='Count', title="Crash Injuries Distribution")
    plotly(fig2)

    crash_type_counts = df['CRASH_TYPE'].value_counts().reset_index()
    crash_type_counts.columns = ['Crash Type', 'Count']
    fig3 = px.pie(crash_type_counts, names='Crash Type', values='Count', title="Distribution of Crash Types")
    plotly(fig3)

    injury_counts = df['INJURIES_TOTAL'].value_counts().reset_index()
    injury_counts.columns = ['Injuries Total', 'Count']
    fig4 = px.pie(injury_counts, names='Injuries Total', values='Count', title="Distribution of Total Injuries")
    plotly(fig4)

