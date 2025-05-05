from preswald import text, plotly, connect, get_df, table, query, slider, selectbox
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('data')

# Check for missing values in the entire DataFrame

df['atk_90_90'] = df['atk_90_90'].fillna(0)
df['def_90_90'] = df['def_90_90'].fillna(0)
df['hp_90_90'] = df['hp_90_90'].fillna(0)
df['special_dish'] = df['special_dish'].fillna("Unknown Dish")
df['region'] = df['region'].fillna("Unknown Region")
df['affiliation'] = df['affiliation'].fillna("Unaffiliated")
df['vision'] = df['vision'].fillna("Not Known")

# Title and Instructions
text("# ⚔️ Genshin Character Explorer")
text("""
Welcome to the **Genshin Character Explorer**! This dashboard allows you to explore character data from Genshin Impact.
Here's how to use it:
1. **Select a Region:** Use the dropdown to choose a region (e.g., Mondstadt).
2. **Select a Weapon Type:**  Optionally, use the dropdown to filter by weapon type (or select 'All').
3. **Set Minimum HP:** Use the slider to filter characters by their HP at level 90.
4. **Explore Data:** View the filtered characters in the table, their regions on the map, and their stats in the radar plot.
""")

# Step 1: User Controls for Interactivity
text("## Step 1: Select Filters")
text("Use the dropdowns and slider below to filter characters by region, weapon type, and HP.")

# Selectbox for Region Selection
regions = ["All"] + df["region"].unique().tolist()
selected_region = selectbox("Select Region", options=regions, default="All")

# Selectbox for Weapon Type Selection
weapon_types = ["All"] + df["weapon_type"].unique().tolist()
selected_weapon_type = selectbox("Select Weapon Type", options=weapon_types, default="All")

# Slider for Minimum HP at Level 90
min_hp_90 = slider("Minimum HP at Level 90", min_val=5000, max_val=16000, default=10000)

# Step 2: SQL Query for Filtering
text("## Step 2: Filtered Character Data")
filter_description = f"Displaying characters"
if selected_region != "All":
    filter_description += f" from **{selected_region}**"
if selected_weapon_type != "All":
    filter_description += f" wielding **{selected_weapon_type}s**"
filter_description += f" with HP >= **{min_hp_90}** at level 90."
text(filter_description)

sql = f"""
SELECT * FROM data
WHERE hp_90_90 >= {min_hp_90}
"""
if selected_region != "All":
    sql += f" AND region = '{selected_region}'"
if selected_weapon_type != "All":
    sql += f" AND weapon_type = '{selected_weapon_type}'"

filtered_df = query(sql, "data")

# Step 3: Display Table for Filtered Data
text("### Character Table")
text("The table below shows the filtered characters, including their name, region, weapon type, and HP.")
table(filtered_df[["character_name" ,"star_rarity" ,"region" ,"vision" ,"weapon_type", "hp_90_90"]])


# Step 5: Grouped Bar Chart for Selected Characters
text("## Step 5: Character Stats Comparison")
text("""
The grouped bar chart below shows the stats of the **top 5 characters by HP** from the filtered data.
- **Stats:** HP, ATK, DEF.
- **Each Character:** Represented by a group of three bars (one for each stat).
Hover over the bars to see the character's name and exact stat values.
""")

# Example: Select top 5 players from filtered data by HP
selected_characters = filtered_df.nlargest(5, "hp_90_90")["character_name"].tolist()
text(f"### Selected Characters: {', '.join(selected_characters)}")

# Filter data for selected players
filtered_characters_df = filtered_df[filtered_df["character_name"].isin(selected_characters)]

# Selected Attributes for Chart - using HP, ATK, DEF at level 90
selected_attributes = ["hp_90_90", "atk_90_90", "def_90_90"]
attribute_names = {
    "hp_90_90": "HP",
    "atk_90_90": "ATK",
    "def_90_90": "DEF"
}# Display friendly names in chart

# Transform data into long format for Plotly
melted_df = filtered_characters_df.melt(id_vars="character_name", value_vars=selected_attributes, 
                                        var_name="Stat", value_name="Value")

# Rename stats for better readability
melted_df["Stat"] = melted_df["Stat"].map(attribute_names)

# Create grouped bar chart
fig_grouped_bar = px.bar(
    melted_df,
    x="character_name",
    y="Value",
    color="Stat",
    title="Top 5 Characters by HP - Comparing HP, ATK, and DEF",
    labels={"character_name": "Character", "Value": "Stat Value"},
    barmode="group"
)

# Show plot
plotly(fig_grouped_bar)

text("## Step 6: Sunburst Chart - Character Distribution")
text("""
This sunburst chart shows how characters are distributed by their **Vision (Element)** and their **Names**.
- **Outer Rings:** Individual characters.
- **Inner Rings:** Vision (Element).
- **Size:** Based on HP at level 90.
Click on a section to zoom in and explore further.
""")

# Creating Sunburst Chart
fig_sunburst = px.sunburst(
    filtered_df,
    path=["vision", "character_name"],
    values="hp_90_90",
    color="vision",
    title="Sunburst Chart: Character Distribution by Vision"
)

# Show Sunburst Chart
plotly(fig_sunburst)