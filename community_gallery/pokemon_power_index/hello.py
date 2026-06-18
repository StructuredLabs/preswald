from preswald import text, plotly, connect, get_df, table, slider, text_input
import plotly.express as px

text("# Pokemon Power Index \U0001f42d\U0001f525")

# Load the CSV
connect()  # load in all sources, which by default is the sample_csv

# Get CSV data
df = get_df("sample_csv")

# Create a strength index adding up all attck, defense, speed, and special points
df["Strength Index"] = df[["Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]].sum(
    axis=1
)

# Sorting types by strength index
df["Overall Power"] = df["Strength Index"].rank(ascending=False)

# Dropping any duoplicate records
df = df.drop_duplicates(subset="Type 1", keep="first")

# Setting up a slider to get how many entries the user wants.
min_pokemon = slider(
    "Overall Power",
    min_val=df["Overall Power"].min(),
    max_val=df["Overall Power"].max(),
    default=410.0,
)

filtered_pokemon_by_power = df[df["Overall Power"] >= min_pokemon]

# Create a scatter plot
fig = px.scatter(
    filtered_pokemon_by_power,
    x="Type 1",
    y="Overall Power",
    title="Most Powerful Types",
    labels={"name": "Type 1", "rank": "Overall Power"},
    color="Type 1",
)

# Add labels for each point
fig.update_traces(textposition="top center", marker=dict(size=12, color="lightblue"))

# Style the plot
fig.update_layout(template="plotly_white")

# Show the plot
plotly(fig)

# Get user text input
user_input = text_input(
    label="Type in a Pokemon you want to see stats on",
    placeholder="Type in the name of the Pokemon here.",
    size=1.5,
)

# Filter the data based on the user input
filtered_input = df[df["Name"].str.contains(user_input, case=False, na=False)]

# Show the data
table(filtered_input)

# Showing power of pokemon in a bar graph
power_share_bar = px.bar(
    df,
    x="Name",
    y="Overall Power",
    labels={"Overall Power": "Overall Power"},
    hover_data=["Type 1", "Overall Power"],
    color=df["Name"],
    title="Most Powerful Pokemon",
)

plotly(power_share_bar)
