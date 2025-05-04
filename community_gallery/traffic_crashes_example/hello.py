import pandas as pd
import plotly.express as px
from preswald import connect, table, text, plotly

# Initialize connection to Preswald service
connect()

# Load the dataset
data_file = "data/Traffic.csv"

try:
    df = pd.read_csv(data_file)

    if df is not None and not df.empty:
        text("✅ **Data loaded successfully!**")

        # Drop NaN values for required columns
        df = df.dropna(subset=['LATITUDE', 'LONGITUDE', 'INJURIES_TOTAL', 'CRASH_TYPE', 'CRASH_DATE'])

        # Scatter plot of crashes by location
        fig = px.scatter(df, x="LATITUDE", y="LONGITUDE", color="CRASH_TYPE", title="🚗 Traffic Crashes by Location and Crash Type")
        plotly(fig)

        # Pie chart for crash types
        crash_type_counts = df['CRASH_TYPE'].value_counts().reset_index()
        crash_type_counts.columns = ['Crash Type', 'Count']
        fig3 = px.pie(crash_type_counts, names='Crash Type', values='Count', title="🚨 Distribution of Crash Types")
        plotly(fig3)

        # Pie chart for injuries total
        injury_counts = df['INJURIES_TOTAL'].value_counts().reset_index()
        injury_counts.columns = ['Injuries Total', 'Count']
        fig4 = px.pie(injury_counts, names='Injuries Total', values='Count', title="🏥 Distribution of Total Injuries")
        plotly(fig4)

        # Convert crash date to datetime for trend analysis
        df['CRASH_DATE'] = pd.to_datetime(df['CRASH_DATE'], errors='coerce')
        df['YEAR'] = df['CRASH_DATE'].dt.year

        # Line chart showing crash trends over the years
        yearly_crash_counts = df.groupby('YEAR').size().reset_index(name='Crash Count')
        fig5 = px.line(yearly_crash_counts, x='YEAR', y='Crash Count', markers=True, title="📉 Crash Trends Over the Years")
        plotly(fig5)

        # 🌍 **World Map - Crash Locations**
        fig6 = px.scatter_geo(df,
                              lat="LATITUDE", lon="LONGITUDE",
                              color="CRASH_TYPE",
                              title="🌍 Traffic Crashes on a World Map",
                              hover_data=["CRASH_TYPE", "INJURIES_TOTAL"],
                              projection="natural earth")

        plotly(fig6)

        # Display a sample of the dataset
        text("🔎 **Data Preview:**")
        table(df[['LATITUDE', 'LONGITUDE', 'CRASH_TYPE', 'INJURIES_TOTAL', 'CRASH_DATE']].head(10))

    else:
        text("⚠️ **Dataset is empty. Please check the file content.**")
