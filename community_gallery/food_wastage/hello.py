from preswald import connect, table, text, slider, plotly,get_df
import plotly.express as px
# from preswald import start_server
# start_server()
connect()

# Load dataset from URL
dataset_url = "/data/global_food_wastage_dataset.csv"
df = get_df(dataset_url)

# App title
text("# Global Food Wastage Analysis (2018-2024)")

# slider filter for Year
min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
selected_year = slider("Select Year", min_val=min_year, max_val=max_year, default=max_year)
filtered_df = df[df["Year"] == selected_year]

# slider filter for Minimum Wastage
min_wastage, max_wastage = int(df["Wastage (tons)"].min()), int(df["Wastage (tons)"].max())
selected_wastage = slider("Minimum Wastage (tons)", min_val=min_wastage, max_val=max_wastage, default=min_wastage)
wastage_filtered_df = filtered_df[filtered_df["Wastage (tons)"] >= selected_wastage]

#filtered datasett
table(wastage_filtered_df, title=f"Food Wastage Data for {selected_year} with Wastage ≥ {selected_wastage} tons")

# Food Wastage Trends by Country- LINE CHART
fig1 = px.line(df, x="Year", y="Wastage (tons)", color="Country", title="Food Wastage Trends by Country")
plotly(fig1)

#Top 5 Countries by Wastage in Selected Year - SCATTER PLOT
top_countries = filtered_df.groupby("Country")["Wastage (tons)"].sum().nlargest(5).reset_index()
fig2 = px.scatter(top_countries, x="Country", y="Wastage (tons)", size="Wastage (tons)", color="Country", title=f"Top 5 Countries by Food Wastage in {selected_year}")
plotly(fig2)

# Food Type Distribution in Selected Year -PIE CHART
fig3 = px.pie(filtered_df, names="Food Type", values="Wastage (tons)", title=f"Food Type Distribution in {selected_year}")
plotly(fig3)

# Wastage by Food Category in Selected Year - SCATTER PLOT.
category_wastage = filtered_df.groupby("Food Type")["Wastage (tons)"].sum().reset_index()
fig4 = px.scatter(category_wastage, x="Food Type", y="Wastage (tons)", size="Wastage (tons)", color="Food Type", title=f"Food Wastage by Category in {selected_year}")
plotly(fig4)

# Top 5 Countries by Average Wastage Weight- SCATTER PLOT
avg_wastage = df.groupby("Country")["Wastage (tons)"].mean().nlargest(5).reset_index()
fig5 = px.scatter(avg_wastage, x="Country", y="Wastage (tons)", size="Wastage (tons)", color="Country", title="Top 5 Countries by Average Food Wastage Weight")
plotly(fig5)
