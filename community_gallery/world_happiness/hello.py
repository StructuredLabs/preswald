from preswald import connect, get_df, table, text, slider, plotly, selectbox, button
import plotly.express as px
import pandas as pd

connect()

df = get_df("world")

if df is None:
    raise ValueError("Failed to load the dataset. Please check the data source configuration.")

df.columns = df.columns.str.strip()

if 'Country name' not in df.columns:
    raise KeyError("'Country name' column not found in the dataset. Available columns are: {}".format(df.columns))

text("# 🌍 World Happiness Analysis App")

years = df['year'].unique()
selected_year = slider("Select Year", min_val=int(years.min()), max_val=int(years.max()), default=int(years.max()))

year_df = df[df['year'] == selected_year]

all_countries = year_df["Country name"].unique()
selected_country = selectbox("Select a Primary Country", ["All Countries"] + list(all_countries))

add_country = button("Add Another Country")

if add_country:
    selected_country_2 = selectbox("Select Another Country", ["None"] + list(all_countries))
    selected_countries = [selected_country]
    if selected_country_2 != "None":
        selected_countries.append(selected_country_2)
else:
    selected_countries = [selected_country]

selected_df = year_df[year_df["Country name"].isin(selected_countries)] if selected_countries else year_df

threshold = slider("Minimum Life Ladder Score", min_val=0, max_val=10, default=5)

filtered_df = selected_df[selected_df["Life Ladder"] > threshold]

table(filtered_df, title="📊 Filtered Happiness Data")

fig1 = px.scatter(
    filtered_df,
    x="Log GDP per capita",
    y="Life Ladder",
    color="Country name",
    title="Life Ladder vs Log GDP per Capita",
    hover_name="Country name"
)
plotly(fig1)

text("## 🔎 Correlation Analysis")
correlation_columns = ["Life Ladder", "Log GDP per capita", "Social support", "Healthy life expectancy at birth"]
correlation_matrix = filtered_df[correlation_columns].corr()
table(correlation_matrix, title="📊 Correlation Table")

top_n = slider("Top N Happiest Countries", min_val=5, max_val=20, default=10)
top_countries = year_df.nlargest(top_n, "Life Ladder")

fig2 = px.bar(
    top_countries,
    x="Country name",
    y="Life Ladder",
    title=f"🏆 Top {top_n} Happiest Countries",
    color="Country name"
)
plotly(fig2)

fig3 = px.line(
    filtered_df,
    x="Country name",
    y="Healthy life expectancy at birth",
    title="📈 Healthy Life Expectancy Across Countries",
    markers=True
)
plotly(fig3)
