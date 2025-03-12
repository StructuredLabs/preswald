from preswald import text, plotly, connect, get_df, table, selectbox, separator, alert
import plotly.express as px

connect()
df = get_df("economic_data")

text("# Analyzing Economic Indicators in BRICS: A Comparative Study")

unique_countries = df[['Country Name', 'Country Code']].drop_duplicates()
series_name = df[['Series Name']].drop_duplicates()
series_name = series_name["Series Name"].tolist()
country_list = list(unique_countries["Country Name"])

text("## Time-Series Analysis of Economic Trends in BRICS Nations")
text("Please select an economic indicator to analyze the time-series data.")

choice_series_name = selectbox(
    label="Select Series Name",
    options=series_name
)

# Convert the year columns to a long format
df_melted = df.melt(id_vars=['Country Name', 'Country Code', 'Series Name'], 
                     var_name='Year', value_name='Value')

# Extract numeric year values
df_melted['Year'] = df_melted['Year'].str.extract(r'(\d{4})').astype(float)
indicator = choice_series_name  # Change as needed
df_filtered = df_melted[df_melted['Series Name'] == indicator]

# Plot the time-series line chart
fig1 = px.line(df_filtered, x="Year", y="Value", color="Country Name",
              title=f"{indicator} Over Time",
              labels={"Value": indicator, "Year": "Year"},
              markers=True)

fig1.show()

plotly(fig1)

separator()

try:
    text("## Comparative Economic Analysis of BRICS Nations")
    text("Please select a year to compare the economic indicators of BRICS nations.")
    
    years = df_filtered['Year'].dropna().unique().tolist()
    choice_year = selectbox(
        label="Select Year",
        options=years
    )

    # Get the most recent year with valid data
    df_filtered = df_filtered.dropna(subset=['Value'])  # Remove NaN values
    # latest_year = df_filtered['Year'].max()

    df_latest = df_filtered[df_filtered['Year'] == choice_year]

    if df_latest.empty:
        print(f"No data available for {indicator} in {int(choice_year)}")
    else:
        # Plot bar chart
        fig2 = px.bar(df_latest, x="Country Name", y="Value", color="Country Name",
                    title=f"{indicator} in {int(choice_year)}",
                    labels={"Value": indicator, "Country Name": "Country"},
                    text_auto='.2s')

        fig2.show()

    plotly(fig2)
except Exception as e:
    alert(message="To display any results, please select a year.", level="critical")
    print(f"An error occurred: {e}")


separator()

text("## BRICS Economic Data Table")
text("The table below shows the economic data for BRICS nations.")

table(df, limit=50)