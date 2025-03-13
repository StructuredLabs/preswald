import pandas as pd
import plotly.express as px

from preswald import connect, get_df, plotly, slider, table, text


# Report Title
text(
    "# Billion-Dollar Disasters \n This report provides a visual analysis of weather and climate-related billion-dollar disasters that have affected the U.S. between 1980 and 2024."
)

# Load the CSV
connect()
df = get_df("disasters_csv")

# Add a new column which calculates the duration of disasters in days (by using "End Date" and "Start Date")
df["Days Duration"] = (
    df["End Date"].apply(lambda x: pd.to_datetime(str(x), format="%Y%m%d"))
    - df["Begin Date"].apply(lambda x: pd.to_datetime(str(x), format="%Y%m%d"))
).dt.days

# Disaster Death Tolls
text(
    "## Disaster Death Tolls \n This bar graph allows us to visualize which disasters correlate with higher death tolls."
)
fig1 = px.bar(df, x="Disaster", y="Deaths", hover_data=["Deaths", "Disaster", "Name"])
fig1.update_layout(template="plotly_white")
plotly(fig1)

# Disaster Cost
text(
    "## Disaster Cost \n This bar graph allows us to visualize which disasters correlate with higher cost."
)
fig2 = px.bar(
    df,
    x="Disaster",
    y="CPI-Adjusted Cost",
    labels={"CPI-Adjusted Cost": "Cost (in millions)"},
    hover_data=["CPI-Adjusted Cost", "Disaster", "Name"],
)
fig2.update_layout(template="plotly_white")
plotly(fig2)

# Sepal Length vs Sepal Width
text(
    "## Deaths in Relation to Cost \n This scatter plot shows the relationship between deaths and CPI-Adjusted Cost. We can see that in most cases, higher cost disasters tend to have higher death tolls."
)
cost_filter = slider(
    "Max cost displayed (lower value = more zoom)",
    min_val=0,
    max_val=220000,
    default=220000,
)
fig3 = px.scatter(
    df[df["CPI-Adjusted Cost"] < cost_filter],
    x="CPI-Adjusted Cost",
    y="Deaths",
    color="Disaster",
    title="Deaths vs Cost (in millions)",
    labels={"CPI-Adjusted Cost": "Cost (in millions)"},
)
fig3.update_layout(template="plotly_white")
plotly(fig3)

# Duration vs Death Toll
text(
    "## Deaths in Relation to Disaster Duration \n This scatter plot shows the relationship between deaths and duration of disaster. We can see that there does not seem to be a correlation. There are 2 outliers: 2 and 5 day Tropical Cyclones."
)
fig4 = px.scatter(
    df,
    x="Days Duration",
    y="Deaths",
    color="Disaster",
    title="Deaths vs Disaster Duration",
)
fig4.update_layout(template="plotly_white")
plotly(fig4)

# Duration vs Cost
text(
    "## Cost in Relation to Disaster Duration \n This scatter plot shows the relationship between cost and duration of disaster. There seems to be a spike of short-lasting cyclones which rack up a high cost."
)
fig5 = px.scatter(
    df,
    x="Days Duration",
    y="CPI-Adjusted Cost",
    color="Disaster",
    title="Cost vs Disaster Duration",
    labels={"CPI-Adjusted Cost": "Cost (in millions)"},
)
fig5.update_layout(template="plotly_white")
plotly(fig5)


# Show the first 10 rows of the dataset
text(
    "## Sample of the Disasters Dataset \n Below is a preview of the first 10 rows of the dataset."
)
table(df, limit=10)
