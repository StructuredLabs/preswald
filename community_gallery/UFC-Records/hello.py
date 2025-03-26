from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import plotly.express as px

 
# Load the CSV dataset defined in preswald.toml under [data.sample_csv]
connect()  # load in all sources
df = get_df('sample_csv')

text("# MMA Fighter Records")

# Option 1: Show full dataset table
#table(df, title="Full Dataset")

# Option 2: Filter dataset by record type (e.g., "Total Fights" or "Wins")
record_type = "Total Fights"  # you can later make this dynamic with a user control

# Filter the DataFrame to show only one record type
filtered_df = df[df["Type of Record"] == record_type]
table(filtered_df, title=f"{record_type} Records")

# Option 3: Add a slider to dynamically filter fighters based on Total value
threshold = slider("Minimum Total", min_val=0, max_val=50, default=30)
dynamic_df = filtered_df[filtered_df["Total"] >= threshold]
table(dynamic_df, title=f"{record_type} with Total ≥ {threshold}")

# Option 4: Create a scatter plot to visualize Rank vs Total
fig = px.scatter(filtered_df, x="Rank", y="Total", hover_data=["Name"],
                 title=f"{record_type} - Rank vs Total")
plotly(fig)