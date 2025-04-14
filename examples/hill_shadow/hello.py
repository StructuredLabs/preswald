import numpy as np
import pandas as pd

# --- Begin Preswald App Code ---
from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.graph_objects as go
import plotly.express as px

# --- Connect to Preswald Data Sources ---
connect()

# --- Load the Terrain Dataset from CSV ---
df = get_df("terrain_pointcloud")

# --- Convert lat/lon to meters for proper scaling ---
lons = df['lon'].values
lats = df['lat'].values
elevs = df['elev'].values

lat_mean = np.mean(lats)
scale_lon = 111320 * np.cos(np.radians(lat_mean))  # meters per degree longitude
scale_lat = 110574  # meters per degree latitude

# --- Create an Interpolation Grid (Without SciPy) ---
grid_size = 80  # Higher resolution for smoother terrain
grid_lon = np.linspace(lons.min(), lons.max(), grid_size)
grid_lat = np.linspace(lats.min(), lats.max(), grid_size)
grid_x, grid_y = np.meshgrid(grid_lon * scale_lon, grid_lat * scale_lat)

# --- Approximate Elevation Interpolation Using NumPy ---
grid_elev = np.zeros_like(grid_x)

for i in range(grid_x.shape[0]):
    for j in range(grid_x.shape[1]):
        distances = np.sqrt((grid_x[i, j] - lons * scale_lon) ** 2 + (grid_y[i, j] - lats * scale_lat) ** 2)
        nearest_idx = np.argmin(distances)
        grid_elev[i, j] = elevs[nearest_idx]

# --- Recenter the Grid for a Balanced 3D View ---
center_x, center_y, center_z = np.mean(grid_x), np.mean(grid_y), np.mean(grid_elev)
grid_x_centered = grid_x - center_x
grid_y_centered = grid_y - center_y
grid_elev_centered = (grid_elev - center_z) * 1.0  # Maintain realistic elevation scaling

# --- Compute Hillshade (For Better Shadows) ---
def compute_hillshade(elevation, azimuth_deg, altitude_deg):
    grad_x = np.gradient(elevation, axis=1)
    grad_y = np.gradient(elevation, axis=0)
    
    slope = np.arctan(np.sqrt(grad_x**2 + grad_y**2))
    aspect = np.arctan2(grad_y, -grad_x)
    
    azimuth_rad = np.radians(360 - azimuth_deg + 90)
    altitude_rad = np.radians(altitude_deg)
    
    hillshade = np.cos(altitude_rad) * np.cos(slope) + np.sin(altitude_rad) * np.sin(slope) * np.cos(azimuth_rad - aspect)
    return np.clip(hillshade * 1.3, 0, 1)  # Adjust contrast for better shadows

# --- Preswald UI Elements ---
text("# 🌍 3D Terrain Visualization with Sun & Water Controls")
text("This app visualizes **actual elevation data** from the CSV with **sun shadows, SQL queries, histograms, scatter plots, and box plots**.")

# --- User Controls for Sun & Water ---
text("### ☀️ Sun & Water Settings")
sun_azimuth = slider("Sun Azimuth (°)", min_val=0, max_val=360, default=315)
sun_altitude = slider("Sun Altitude (°)", min_val=0, max_val=90, default=45)
water_level = slider("Water Level (m)", min_val=200, max_val=400, default=250)

# --- Compute Hillshade & Water Surface ---
hillshade = compute_hillshade(grid_elev, sun_azimuth, sun_altitude)
hillshade_bright = np.clip(hillshade + 0.2, 0, 1)

water_surface = np.where(grid_elev < water_level, water_level, np.nan)
water_surface_centered = water_surface - center_z

# --- Compute Sun Marker Position ---
azimuth_rad = np.radians(360 - sun_azimuth + 90)
altitude_rad = np.radians(sun_altitude)

# Place sun at a realistic distance based on terrain height
terrain_height = grid_elev_centered.max() - grid_elev_centered.min()
D_xy = terrain_height * 3  # Distance based on terrain height
D_z = terrain_height * 2   # Keep sun sufficiently above terrain

sun_dir = np.array([np.cos(altitude_rad) * np.cos(azimuth_rad),
                    np.cos(altitude_rad) * np.sin(azimuth_rad),
                    np.sin(altitude_rad)])

sun_x, sun_y, sun_z = D_xy * sun_dir[0], D_xy * sun_dir[1], D_z * sun_dir[2]

# --- Build 3D Terrain Figure with Proper Scaling ---
fig = go.Figure()

# Terrain surface using actual CSV elevation data
fig.add_trace(go.Surface(
    x=grid_x_centered,
    y=grid_y_centered,
    z=grid_elev_centered,
    surfacecolor=hillshade_bright,
    colorscale="earth",  # Smoother color gradient
    cmin=0,
    cmax=1,
    colorbar=dict(title="Terrain Shading"),
    showscale=True
))

# Water surface overlay
fig.add_trace(go.Surface(
    x=grid_x_centered,
    y=grid_y_centered,
    z=water_surface_centered,
    colorscale=[[0, 'rgba(0,0,255,0.5)'], [1, 'rgba(0,0,255,0.5)']],  # More subtle water layer
    showscale=False,
    opacity=0.6
))

# Sun marker
fig.add_trace(go.Scatter3d(
    x=[sun_x], y=[sun_y], z=[sun_z],
    mode='markers',
    marker=dict(size=15, color='gold', symbol='circle'),  # Proper sun scaling
    name='Sun ☀️'
))

# --- Camera & Layout Adjustments for Correct Scaling ---
fig.update_layout(
    title=f"🌄 3D Terrain (Azimuth: {sun_azimuth}°, Altitude: {sun_altitude}°), Water Level: {water_level} m",
    scene=dict(
        xaxis_title='X (m)',
        yaxis_title='Y (m)',
        zaxis_title='Elevation (m)',
        aspectmode="manual",
        aspectratio=dict(x=1, y=1, z=0.5),  # **More natural terrain appearance**
        camera=dict(eye=dict(x=2, y=2, z=1.5))  # Adjusted for better perspective
    ),
    autosize=False, width=900, height=700,
    legend=dict(x=0.05, y=0.95, xanchor="left", yanchor="top")
)

plotly(fig)



# --- SQL Query on Terrain Data ---
text("## 📊 Querying Terrain Data")
elev_threshold = slider("Elevation Threshold for SQL Query (m)", 
                          min_val=int(df['elev'].min()), 
                          max_val=int(df['elev'].max()), 
                          default=250)

sql = f"""
SELECT lat, lon, elev, temperature, moisture, vegetation_index
FROM terrain_pointcloud 
WHERE elev > {elev_threshold}
"""
sql_df = query(sql, "terrain_pointcloud")
table(sql_df, title=f"🔍 Points with Elevation > {elev_threshold} m")

# --- Histogram of Elevation Distribution ---
text("## 📈 Elevation Distribution")
fig_hist = px.histogram(df, x="elev", nbins=30, title="Histogram of Elevation Data")
plotly(fig_hist)

# --- Scatter Plot (Elevation vs Temperature) ---
text("## 🌡️ Elevation vs Temperature")
fig_scatter = px.scatter(df, x="elev", y="temperature", color="vegetation_index",
                         title="Scatter Plot: Elevation vs Temperature (colored by Vegetation Index)",
                         labels={"elev": "Elevation (m)", "temperature": "Temperature (°C)"})
plotly(fig_scatter)

# --- Box Plot of Moisture Distribution ---
text("## 💧 Moisture Analysis")
fig_box = px.box(df, y="moisture", title="Box Plot of Moisture Levels",
                 labels={"moisture": "Moisture (%)"})
plotly(fig_box)
