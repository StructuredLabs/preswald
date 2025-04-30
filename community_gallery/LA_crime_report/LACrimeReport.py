from preswald import (
    text, plotly, connect, get_df, table, slider, selectbox, alert, checkbox, 
    separator, button, image
)
import plotly.express as px

# Initialize the app
text("# Los Angeles Crime Report Analysis")
image("https://picsum.photos/1200/400?grayscale")  
text("Explore crime data in Los Angeles. 🚔")

# Load the dataset
connect()  
df = get_df("LACrimeReport_csv")  # Load the dataset

# Display raw data
text("## Raw Data")
table(df.head())

# Add a separator
separator()

# Add user controls -  Filter by crime time (Slider)
text("## Dynamic Data View: Filter by Crime Time")
threshold = slider("Crime Time (24-hour format)", min_val=0, max_val=2359, default=1200)


# Filter the DataFrame based on the threshold
filtered_time_df = df[df["TIME OCC"] > threshold]
table(filtered_time_df, title=f"Crimes After {threshold} Hours")

# Add a checkbox to enable/disable crime type
text("## Filter by Crime Type")
enable_crime_type_filter = checkbox("Enable Crime Type Filter", default=True)

if enable_crime_type_filter:
    crime_types = df["Crm Cd Desc"].unique().tolist()
    selected_crime_type = selectbox("Select Crime Type", options=crime_types, default=crime_types[0])
    filtered_crime_type_df = df[df["Crm Cd Desc"] == selected_crime_type]
    text(f"## Crime Count by Area for '{selected_crime_type}'")
    crime_count_by_area = filtered_crime_type_df["AREA NAME"].value_counts().reset_index()
    crime_count_by_area.columns = ["Area Name", "Crime Count"]
    fig1 = px.bar(crime_count_by_area, x="Area Name", y="Crime Count", 
                  title=f"Crime Count by Area for '{selected_crime_type}'", 
                  labels={"Area Name": "Area", "Crime Count": "Number of Crimes"})
    fig1.update_layout(template='plotly_white')

    plotly(fig1)
else:
    alert("Crime type filter is disabled.")

# Add a separator
separator()

# Add user controls: Filter by area
text("## Filter by Area")
areas = df["AREA NAME"].unique().tolist()
selected_area = selectbox("Select Area", options=areas, default=areas[0])
filtered_area_df = df[df["AREA NAME"] == selected_area]

text(f"## Crime Types in '{selected_area}'")
crime_types_by_area = filtered_area_df["Crm Cd Desc"].value_counts().reset_index()
crime_types_by_area.columns = ["Crime Type", "Count"]
fig2 = px.pie(crime_types_by_area, names="Crime Type", values="Count", 
              title=f"Crime Types in '{selected_area}'")

fig2.update_layout(template='plotly_white')
plotly(fig2)

separator()

# Add user controls: Filter by victim age
text("## Filter by Victim Age")
victim_age = slider("Victim Age", min_val=0, max_val=100, default=30)

filtered_age_df = df[df["Vict Age"] == victim_age]
text(f"## Crime Types for Victim Age {victim_age}")
fig3 = px.histogram(filtered_age_df, x="Crm Cd Desc", 
                    title=f"Crime Types for Victim Age {victim_age}", 
                    labels={"Crm Cd Desc": "Crime Type"})

fig3.update_layout(template='plotly_white')

plotly(fig3)

separator()

# Add user controls: Filter by weapon used
text("## Filter by Weapon Used")
weapons = df["Weapon Desc"].dropna().unique().tolist()
selected_weapon = selectbox("Select Weapon", options=weapons, default=weapons[0])

filtered_weapon_df = df[df["Weapon Desc"] == selected_weapon]

text(f"## Crime Locations for '{selected_weapon}'")
fig4 = px.scatter(filtered_weapon_df, x="LON", y="LAT", color="AREA NAME", 
                  title=f"Crime Locations for '{selected_weapon}'",
                  labels={"LON": "Longitude", "LAT": "Latitude", "AREA NAME": "Area"})

fig4.update_layout(template='plotly_white')
plotly(fig4)

separator()

# Create a visualization: Scatter plot of crime locations
text("## Crime Locations")
fig5 = px.scatter(df, x="LON", y="LAT", color="AREA NAME", 
                 title="Crime Locations in Los Angeles",
                 labels={"LON": "Longitude", "LAT": "Latitude", "AREA NAME": "Area"})

fig5.update_layout(template='plotly_white')
plotly(fig5)

separator()

# Create a bar chart: Crime count by area
text("## Crime Count by Area")
crime_count_by_area = df["AREA NAME"].value_counts().reset_index()
crime_count_by_area.columns = ["Area Name", "Crime Count"]
fig6 = px.bar(crime_count_by_area, x="Area Name", y="Crime Count", 
              title="Crime Count by Area", 
              labels={"Area Name": "Area", "Crime Count": "Number of Crimes"})

fig6.update_layout(template='plotly_white')
plotly(fig6)

if button("Refresh Data"):
    df = get_df("LACrimeReport_csv")  # Reload the dataset
    alert("Data refreshed successfully!")