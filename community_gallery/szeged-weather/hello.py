import plotly.express as px
from preswald import text, connect, get_df, table, query, slider, plotly

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')
    
# Step 1 completed
sql = 'SELECT * FROM sample_csv WHERE "Temperature (C)" < 10.0'
filtered_df = query(sql, "sample_csv")

# Step 2 completed
# text("This is your first app. 🎉")
text("# My Szeged Weather Analysis App!")
table(filtered_df, title="Filtered Data")

if table:
    text("Table generated successfully")
else:
    text("Table did not generate successfully")

threshold = slider(
    "Filter by Temperature (C)",
    min_val=df["Temperature (C)"].min(),
    max_val=df["Temperature (C)"].max(),
    default=10,
)

filtered_dynamic_df = df[df["Temperature (C)"] > threshold]
table(filtered_dynamic_df, title="Dynamic Data View")

# Step 3 completed

fig = px.scatter(
    filtered_dynamic_df,
    x="Formatted Date",
    y="Temperature (C)",
    title="Temperature (C) Over Time",
    labels={'Formatted Date': 'Formatted Date', 'Temperature (C)': 'Temperature (C)'}
)

plotly(fig)

# Step 4 completed