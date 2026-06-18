from preswald import connect, get_df, query, table, text, plotly, slider, selectbox
import plotly.express as px
import plotly.graph_objects as go

# Initialize connection
connect()

# Load dataset
df = get_df("netflix_titles")

# Title and Instructions
text("# TV Show and Movie Explorer")
text("""Welcome to the **TV Show & Movie Explorer!** This dashboard helps you discover content from Netflix.

Here's how to use it:

1. Select a **Type**: Use the dropdown to choose a genre (e.g., TV Show, Movie).
2. Set Minimum **Release Year**: Use the slider to filter titles based on their Release year.
3. Explore Content: View the filtered movies and shows in the table, including their release years on the timeline, and their key details in the info panel.  
""")

# 🔍 Step 1: User Controls for Interactivity
text("### Step 1: Select a Type and Set Filters")
text("Use the dropdown and slider below to filter Type and Release Year.")

# Selectbox for Club Selection
selected_club = selectbox("Select Type", options=df["type"].unique().tolist(), default="Movie")

# Slider for Minimum Overall Rating
min_overall_rating = slider("Minimum Release Year", min_val=2000, max_val=2025, default=2010)

# 🔍 Step 2: SQL Query for Filtering
text("### Step 2: Filtered Type Data")
text(f"Displaying **{selected_club}** with Release Year >= **{min_overall_rating}**.")

sql = f"""
SELECT * FROM netflix_titles 
WHERE "type" = '{selected_club}' 
AND release_year >= {min_overall_rating}
"""
filtered_df = query(sql, "netflix_titles")

# 🔍 Step 3: Display Table for Filtered Data
text("#### Details Table")
text("The table below shows the filtered movies, tv show, including their type, title, director, country, release_year, rating.")
table(filtered_df[['type','title','director','country','release_year','rating']])

# 🔍 Step 4: Map with Player Locations
text(f"### Step 3: {selected_club} Locations on Map")
text(f"""The map below shows the locations of the filtered {selected_club}.    
Hover over a point to see the country's name.  
""")

# Map: Size = Overall Rating, Color = Role
fig_map = px.scatter_geo(filtered_df, locations="country", locationmode="country names",
                         title=f"🌍 {selected_club} Location",
                         color_discrete_sequence=px.colors.qualitative.Plotly)  # Use a color palette for roles

# Display Map
plotly(fig_map)
