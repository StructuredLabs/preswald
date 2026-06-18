import pandas as pd
import plotly.express as px
from preswald import connect, get_df, plotly, text, table

# Title
text("# Daily Drug Count by Date Reported to CMS")
text("## Analyzing newly reported drugs from March 3-9, 2025")

# Connect to Preswald
connect()

# Load data from URL
url = "https://download.medicaid.gov/data/mdrp-newly-rprt-drug-03-03-2025-to-03-09-2025.csv"
try:
    df = pd.read_csv(url)
    text(f"CSV loaded successfully! Total rows: {len(df)}")
except Exception as e:
    text(f"Error loading CSV: {e}")
    df = pd.DataFrame()

# Process data
if not df.empty and "Date Reported to CMS" in df.columns:
    # df["Date Reported to CMS"] = pd.to_datetime(df["Date Reported to CMS"], errors="coerce")
    daily_counts = df.groupby("Date Reported to CMS").size().reset_index(name="Drug Count")
    
    # Show raw data table
    table(daily_counts)

    # Bar chart
    text("## Daily Drug Counts Chart")
    fig_bar = px.bar(
        daily_counts,
        x="Date Reported to CMS",
        y="Drug Count",
        title="Daily Drug Count (March 3-9, 2025)",
        labels={"Date Reported to CMS": "Date of Reported", "Drug Count": "Number of Drugs"},
        text_auto=True,
    )
    plotly(fig_bar)  # Render the chart inside Preswald
    
else:
    text("Error: 'Date Reported to CMS' column not found or empty dataset.")
