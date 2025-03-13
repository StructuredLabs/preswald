import plotly.express as px
import plotly.graph_objects as go

from preswald import connect, get_df, plotly, query, selectbox, slider, table, text


# Initialize connection
connect()

# Load dataset
df = get_df("data")

# Title and Instructions
text("# ⚽ Club-Based Player Explorer")
text("""
Welcome to the **Club-Based Player Explorer**! This dashboard allows you to explore player data from FIFA 23.  
Here's how to use it:  
1. **Select a Club:** Use the dropdown to choose a club (e.g., Paris Saint-Germain).  
2. **Set Minimum Overall Rating:** Use the slider to filter players by their overall rating.  
3. **Explore Data:** View the filtered players in the table, their locations on the map, and their strengths in the radar plot.  
""")

# 🔍 Step 1: User Controls for Interactivity
text("## Step 1: Select a Club and Set Filters")
text("Use the dropdown and slider below to filter players by club and overall rating.")

# Selectbox for Club Selection
selected_club = selectbox(
    "Select Club",
    options=df["Club Name"].unique().tolist(),
    default="Paris Saint-Germain",
)

# Slider for Minimum Overall Rating
min_overall_rating = slider(
    "Minimum Overall Rating", min_val=0, max_val=100, default=80
)

# 🔍 Step 2: SQL Query for Filtering
text("## Step 2: Filtered Player Data")
text(
    f"Displaying players from **{selected_club}** with an overall rating >= **{min_overall_rating}**."
)

sql = f"""
SELECT * FROM data 
WHERE "Club Name" = '{selected_club}' 
AND Overall >= {min_overall_rating}
"""
filtered_df = query(sql, "data")

# 🔍 Step 3: Display Table for Filtered Data
text("### Player Table")
text(
    "The table below shows the filtered players, including their names, nationalities, and overall ratings."
)
table(filtered_df[["Known As", "Nationality", "Overall"]])

# 🔍 Step 4: Map with Player Locations
text("## Step 3: Player Locations on Map")
text("""
The map below shows the locations of the filtered players.  
- **Size of Points:** Represents the player's overall rating (larger = higher rating).  
- **Color of Points:** Indicates the player's role (e.g., Forward, Midfielder, Defender).  
Hover over a point to see the player's name, role, and rating.  
""")

# Map: Size = Overall Rating, Color = Role
fig_map = px.scatter_geo(
    filtered_df,
    locations="Nationality",
    locationmode="country names",
    size="Overall",
    hover_name="Known As",
    color="Best Position",
    title=f"🌍 Player Locations from {selected_club}",
    color_discrete_sequence=px.colors.qualitative.Plotly,
)  # Use a color palette for roles

# Display Map
plotly(fig_map)

# 🔍 Step 5: Radar Plot for Selected Players
text("## Step 4: Player Strengths (Radar Plot)")
text("""
The radar plot below shows the strengths of the **top 5 players** from the filtered data.  
- **Attributes:** Pace, Shooting, Dribbling, Passing, Defending, Physicality.  
- **Each Player:** Represented by a filled shape on the radar plot.  
Hover over the plot to see the player's name and attribute values.  
""")

# Example: Select top 5 players from filtered data
selected_players = filtered_df.nlargest(5, "Overall")["Known As"].tolist()
text(f"### Selected Players: {', '.join(selected_players)}")

# Filter data for selected players
filtered_players_df = filtered_df[filtered_df["Known As"].isin(selected_players)]

# Selected Attributes for Radar Chart
selected_attributes = [
    "Pace Total",
    "Shooting Total",
    "Dribbling Total",
    "Passing Total",
    "Defending Total",
    "Physicality Total",
]

# Radar Chart
fig_radar = go.Figure()

# Add a trace for each selected player
for _, row in filtered_players_df.iterrows():
    fig_radar.add_trace(
        go.Scatterpolar(
            r=[row[attr] for attr in selected_attributes],  # Attribute values
            theta=selected_attributes,  # Attribute names
            fill="toself",  # Fill the area under the line
            name=row["Known As"],  # Player name
        )
    )

# Update layout for better readability
fig_radar.update_layout(
    title=f"📈 Player Strengths: {', '.join(selected_players)}",
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 100])  # Set axis range for consistency
    ),
    showlegend=True,  # Show legend with player names
)

# Display Radar Chart
plotly(fig_radar)
