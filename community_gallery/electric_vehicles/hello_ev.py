from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px

# Loading the csv
connect()  # Initialize connection to preswald.toml data sources
df = get_df("ev_csv")

# Filters the data for cars that aren't Tesla's
sql = "SELECT * FROM ev_csv WHERE Make != 'TESLA'"
filtered_df = query(sql, "ev_csv")

# Table displaying vehicles other than Tesla's
text("# Electric Vehicle Analysis App")
table(filtered_df, title="Vehicles other than Tesla's:")

# User Controls for electric vehicle range
threshold = slider("Vehicle Range (miles)", min_val=0, max_val=250,
                   default=200)
table(df[df["Electric Range"] > threshold], title="Dynamic Data View")

# Filters the data for model year and vehicle range
sql2 = 'SELECT "Model Year", "Electric Range" FROM ev_csv WHERE "Electric ' \
    'Range" != 0'
filtered_df2 = query(sql2, "ev_csv")

# Visualisation of the model year vs the vehicle range
fig = px.scatter(filtered_df2,
                 x="Model Year",
                 y="Electric Range",
                 title="Model Year vs Vehicle Range")
plotly(fig)
