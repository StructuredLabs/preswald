from preswald import connect, get_df, query, text, table, plotly, text_input, button
import plotly.express as px
import pandas as pd

# Connect & Load Data
task_data = "olympics_csv"
connect()
df = get_df(task_data)
df = df if df is not None else pd.DataFrame()

text("# Olympics Medal Analysis (1896-2024)")

# Input fields
selected_year = text_input("Enter Year (e.g., 2020)").strip()
selected_country = text_input("Enter Country Code (e.g., USA)").strip().upper()
min_medals = text_input("Enter Minimum Medals (e.g., 10)").strip()

# Ensure min_medals is a valid number
min_medals = int(min_medals) if min_medals.isdigit() else 0

sql_query = f"""
SELECT * FROM {task_data}
WHERE 1=1
{f"AND CAST(Year AS TEXT) LIKE '%{selected_year}%'" if selected_year else ""}
{f"AND NOC LIKE '%{selected_country}%'" if selected_country else ""}
{f"AND (Gold + Silver + Bronze) >= {min_medals}" if min_medals > 0 else ""}
"""

filtered_df = query(sql_query, task_data)

if not filtered_df.empty:
    table(filtered_df, title="Filtered Results")

    # Medal Distribution Bar Chart
    if {"Gold", "Silver", "Bronze"}.issubset(filtered_df.columns):
        fig = px.bar(
            x=["Gold", "Silver", "Bronze"],
            y=[filtered_df["Gold"].sum(), filtered_df["Silver"].sum(), filtered_df["Bronze"].sum()],
            labels={"x": "Medal Type", "y": "Count"},
            title="Medal Distribution"
        )
        plotly(fig)

        # Scatter Plot: Total Medals Over the Years
        if "Year" in filtered_df.columns:
            filtered_df["Total Medals"] = filtered_df["Gold"] + filtered_df["Silver"] + filtered_df["Bronze"]
            scatter_years = px.scatter(
                filtered_df,
                x="Year",
                y="Total Medals",
                color="NOC",
                title="Total Medals Over the Years",
                labels={"Year": "Olympic Year", "Total Medals": "Total Count"}
            )
            plotly(scatter_years)

        # Scatter Plot: Gold Medals vs Total Medals
        if {"Gold", "Total Medals"}.issubset(filtered_df.columns):
            scatter_gold = px.scatter(
                filtered_df,
                x="Gold",
                y="Total Medals",
                color="NOC",
                title="Gold Medals vs Total Medals",
                labels={"Gold": "Gold Medals", "Total Medals": "Total Medal Count"},
                size="Total Medals",
                hover_data=["Year"]
            )
            plotly(scatter_gold)

    else:
        text("No relevant data found.")
else:
    text("No relevant data found.")
