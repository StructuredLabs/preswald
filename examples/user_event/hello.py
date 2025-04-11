import plotly.express as px

from preswald import connect, get_df, plotly, table, text


text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the JSON source defined as "user_events" in preswald.toml
connect()  # This loads all data sources, including our nested JSON source.
df = get_df("user_events")

# Create a scatter plot using the flattened data.
# Assuming the JSON file has been flattened to include "user" and "details.clicks"
fig = px.scatter(
    df,
    x="user",
    y="details.clicks",
    text="user",
    title="User Events: Clicks per User",
    labels={"user": "User", "details.clicks": "Clicks"},
)

# Add labels for each point
fig.update_traces(textposition="top center", marker=dict(size=12, color="lightblue"))

# Style the plot
fig.update_layout(template="plotly_white")

# Display the plot
plotly(fig)

# Display the DataFrame as a table
table(df)
