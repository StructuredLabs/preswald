from preswald import connect, get_df, table, text, selectbox, plotly, separator, checkbox
import pandas as pd
import random
import shapely.wkt
import plotly.graph_objects as go
import numpy as np

# Function to convert NumPy int64/float64 to Python int/float for JSON serialization
def convert_dtypes(df):
    for col in df.columns:
        if df[col].dtype == np.int64:
            df[col] = df[col].astype(int)
        elif df[col].dtype == np.float64:
            df[col] = df[col].astype(float)
    return df

# Connect to data sources
connect()

# Add a heading
text("# Swiss Apartment Models Dataset")

# Load the geometries dataset
geometries_df = get_df('geometries')

# Convert NumPy types to Python types to avoid JSON serialization issues
geometries_df = convert_dtypes(geometries_df)

# Create a truncated version of the dataframe for display
display_df = geometries_df.head(2).copy()
# Truncate the geometry column to 50 characters for better display
display_df['geometry'] = display_df['geometry'].apply(lambda x: str(x)[:50] + "..." if len(str(x)) > 50 else x)

# Display first two rows with truncated geometry
text("## Sample Data:")
table(display_df)

# Describe the dataset - using size parameter for compact layout
text("## Dataset Description:", size=1.0)
text("This dataset contains 2D geometry information for apartment elements including:", size=1.0)
# Place the description items side by side
text("- Areas (rooms, bathrooms, kitchens)", size=0.2)
text("- Separators (walls, railings)", size=0.2)
text("- Openings (windows, doors)", size=0.2)
text("- Features (sinks, toilets, bathtubs)", size=0.2)
text("Each element includes spatial data in WKT format and hierarchical information about its location within the building.", size=1.0)

# Analyze hierarchical structure
text("## Hierarchical Structure Analysis:")

# Check and count hierarchy levels
site_count = geometries_df['site_id'].nunique()
building_count = geometries_df.groupby('site_id')['building_id'].nunique().mean()
floor_count = geometries_df.groupby('building_id')['floor_id'].nunique().mean()
apartment_count = geometries_df.groupby('floor_id')['apartment_id'].nunique().mean()
area_count = geometries_df.groupby('apartment_id')['area_id'].nunique().mean()

# Convert NumPy types to Python types
site_count = int(site_count)
building_count = float(building_count)
floor_count = float(floor_count)
apartment_count = float(apartment_count)
area_count = float(area_count)

# Display the hierarchy with compact layout
text("The dataset follows this hierarchical structure:", size=1.0)
text(f" Sites ({site_count} total)", size=0.1)
text(f" Buildings (avg. {building_count:.1f} per site)", size=0.1)
text(f" Floors (avg. {floor_count:.1f} per building)", size=0.1)
text(f" Apartments (avg. {apartment_count:.1f} per floor)", size=0.1)
text(f" Areas/Rooms (avg. {area_count:.1f} per apartment)", size=0.1)
text(f" Features (sinks, toilets, etc.)", size=0.1)

# Show distribution of entity types
separator()
text("## Entity Type Distribution")
entity_type_counts = geometries_df['entity_type'].value_counts()
entity_type_counts = convert_dtypes(entity_type_counts.reset_index().rename(columns={'index': 'Entity Type', 'entity_type': 'Count'}))
table(entity_type_counts)

# Get unique apartment IDs and convert to list of Python native types
unique_apartments = [str(apt) for apt in geometries_df['apartment_id'].dropna().unique()]

# Apartment Viewer section
text("## Apartment Viewer")
text(f"Total unique apartments: {len(unique_apartments)}")

# Sample 10 random apartments for selection
if unique_apartments:
    sample_apartments = random.sample(unique_apartments, min(10, len(unique_apartments)))
    sample_apartments.sort()  # Sort for better user experience

    # Create a selection box
    selected_apartment = selectbox("Select an apartment to view:", options=sample_apartments)

    if selected_apartment:
        # Filter geometries for the selected apartment
        apartment_data = geometries_df[geometries_df['apartment_id'] == selected_apartment]
        text(f"### Apartment {selected_apartment}")
        text(f"Total elements: {len(apartment_data)}")
        
        # Add legend toggle
        show_legend = checkbox("Show entity type legend", default=False)
        
        # Create a Plotly figure
        fig = go.Figure()
        
        # Color mapping for different entity types
        colors = {
            'area': 'rgba(135, 206, 250, 0.3)',      # Light blue with transparency
            'separator': 'rgba(105, 105, 105, 0.8)',  # Dark gray
            'opening': 'rgba(255, 255, 255, 0.9)',    # White with transparency
            'feature': 'rgba(50, 205, 50, 0.6)'       # Green with transparency
        }
        
        # Process each geometry and add to the plot
        for _, row in apartment_data.iterrows():
            try:
                # Parse WKT geometry
                geom = shapely.wkt.loads(row['geometry'])
                
                # Get x, y coordinates (handling both Polygon and LineString types)
                if geom.geom_type == 'Polygon':
                    x, y = zip(*geom.exterior.coords)
                elif geom.geom_type == 'LineString':
                    x, y = zip(*geom.coords)
                else:
                    # Skip other geometry types
                    continue
                
                # Get color based on entity type
                color = colors.get(row['entity_type'], 'rgba(180, 180, 180, 0.5)')
                
                # Add shape to plot
                if geom.geom_type == 'Polygon':
                    fig.add_trace(go.Scatter(
                        x=x, y=y,
                        fill='toself',
                        fillcolor=color,
                        line=dict(color='rgba(50, 50, 50, 0.8)', width=1),
                        name=f"{row['entity_type']} - {row['entity_subtype']}",
                        showlegend=show_legend
                    ))
                else:  # LineString
                    fig.add_trace(go.Scatter(
                        x=x, y=y,
                        mode='lines',
                        line=dict(color=color, width=2),
                        name=f"{row['entity_type']} - {row['entity_subtype']}",
                        showlegend=show_legend
                    ))
            except Exception as e:
                # Skip invalid geometries
                continue
        
        # Update layout
        fig.update_layout(
            title=f"APT Plan",
            autosize=True,
            height=600,
            xaxis=dict(
                scaleanchor="y",
                scaleratio=1,
                showgrid=False
            ),
            yaxis=dict(
                showgrid=False
            ),
            margin=dict(l=0, r=0, b=0, t=40),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Display the plot
        plotly(fig)

# Site -> Building -> Floor -> Apartment Navigation
separator()
text("## Site Navigator", size=1.0)
text("Navigate through the hierarchy: Site → Building → Floor → View", size=1.0)

# Get unique site IDs and convert to list of Python native types
unique_sites = list(geometries_df['site_id'].dropna().unique())
unique_sites = [str(site) for site in unique_sites]

if unique_sites:
    # Sample 10 sites
    sample_sites = random.sample(unique_sites, min(10, len(unique_sites)))
    sample_sites.sort()

    # Create site selection box
    selected_site = selectbox("Select a site:", options=sample_sites)

    if selected_site:
        # Convert selected_site back to original type for filtering
        # Try both string and numeric filtering to handle different types
        try:
            # Try filtering as string first
            site_data = geometries_df[geometries_df['site_id'] == selected_site]
            
            # If no results, try converting to int or float
            if len(site_data) == 0:
                try:
                    site_data = geometries_df[geometries_df['site_id'] == int(selected_site)]
                except ValueError:
                    try:
                        site_data = geometries_df[geometries_df['site_id'] == float(selected_site)]
                    except ValueError:
                        pass
        except:
            text("Error filtering by site ID", size=1.0)
            site_data = pd.DataFrame()
        
        # Get buildings for the selected site
        unique_buildings = list(site_data['building_id'].dropna().unique())
        unique_buildings = [str(bldg) for bldg in unique_buildings]
        
        # Debug info
        text(f"Site {selected_site} has {len(unique_buildings)} buildings", size=1.0)
        
        if len(unique_buildings) == 0:
            text("No buildings found for this site. Debugging info:", size=1.0)
            text(f"Site ID type: {type(selected_site)}", size=0.5)
            text(f"First few site_id types in data: {type(geometries_df['site_id'].iloc[0])}", size=0.5)
            
            # Show a small sample of site_ids from the data for debugging
            site_samples = geometries_df['site_id'].sample(min(5, len(geometries_df))).tolist()
            text(f"Sample site_ids from data: {site_samples}", size=1.0)
        
        # Sample buildings if more than 10
        if len(unique_buildings) > 10:
            sample_buildings = random.sample(unique_buildings, 10)
            sample_buildings.sort()
        else:
            sample_buildings = sorted(unique_buildings)
        
        if len(sample_buildings) > 0:
            # Create building selection box
            selected_building = selectbox("Select a building:", options=sample_buildings)
            
            if selected_building:
                # Similar type handling for building ID
                try:
                    building_data = site_data[site_data['building_id'] == selected_building]
                    if len(building_data) == 0:
                        try:
                            building_data = site_data[site_data['building_id'] == int(selected_building)]
                        except ValueError:
                            try:
                                building_data = site_data[site_data['building_id'] == float(selected_building)]
                            except ValueError:
                                pass
                except:
                    text("Error filtering by building ID", size=1.0)
                    building_data = pd.DataFrame()
                
                # Get floors for the selected building
                unique_floors = list(building_data['floor_id'].dropna().unique())
                unique_floors = [str(floor) for floor in unique_floors]
                
                # Sample floors if more than 10
                if len(unique_floors) > 10:
                    sample_floors = random.sample(unique_floors, 10)
                    sample_floors.sort()
                else:
                    sample_floors = sorted(unique_floors)
                
                # Create floor selection box
                text(f"Building {selected_building} has {len(unique_floors)} floors", size=1.0)
                
                if len(sample_floors) > 0:
                    selected_floor = selectbox("Select a floor:", options=sample_floors)
                    
                    if selected_floor:
                        # Similar type handling for floor ID
                        try:
                            floor_data = building_data[building_data['floor_id'] == selected_floor]
                            if len(floor_data) == 0:
                                try:
                                    floor_data = building_data[building_data['floor_id'] == int(selected_floor)]
                                except ValueError:
                                    try:
                                        floor_data = building_data[building_data['floor_id'] == float(selected_floor)]
                                    except ValueError:
                                        pass
                        except:
                            text("Error filtering by floor ID", size=1.0)
                            floor_data = pd.DataFrame()
                        
                        # Get apartments for the selected floor
                        unique_apartments = list(floor_data['apartment_id'].dropna().unique())
                        unique_apartments = [str(apt) for apt in unique_apartments]
                        
                        # Create view type selection
                        text(f"Floor {selected_floor} has {len(unique_apartments)} apartments", size=1.0)
                        
                        view_type = selectbox("Select view type:", options=["Full Floor", "Single Apartment"])
                
                        if view_type == "Full Floor":
                            # Show full floor plan
                            text(f"### Full Floor Plan - Floor {selected_floor}")
                            text(f"Total elements: {len(floor_data)}")
                            
                            # Add legend toggle
                            show_legend = checkbox("Show entity type legend", default=False)
                            
                            # Create floor plan
                            fig = go.Figure()
                            
                            # Process each geometry and add to the plot
                            for _, row in floor_data.iterrows():
                                try:
                                    # Parse WKT geometry
                                    geom = shapely.wkt.loads(row['geometry'])
                                    
                                    # Get x, y coordinates (handling both Polygon and LineString types)
                                    if geom.geom_type == 'Polygon':
                                        x, y = zip(*geom.exterior.coords)
                                    elif geom.geom_type == 'LineString':
                                        x, y = zip(*geom.coords)
                                    else:
                                        # Skip other geometry types
                                        continue
                                    
                                    # Get color based on entity type
                                    color = colors.get(row['entity_type'], 'rgba(180, 180, 180, 0.5)')
                                    
                                    # Add shape to plot
                                    if geom.geom_type == 'Polygon':
                                        fig.add_trace(go.Scatter(
                                            x=x, y=y,
                                            fill='toself',
                                            fillcolor=color,
                                            line=dict(color='rgba(50, 50, 50, 0.8)', width=1),
                                            name=f"{row['entity_type']} - {row['entity_subtype']}",
                                            showlegend=show_legend
                                        ))
                                    else:  # LineString
                                        fig.add_trace(go.Scatter(
                                            x=x, y=y,
                                            mode='lines',
                                            line=dict(color=color, width=2),
                                            name=f"{row['entity_type']} - {row['entity_subtype']}",
                                            showlegend=show_legend
                                        ))
                                except Exception as e:
                                    # Skip invalid geometries
                                    continue
                            
                            # Update layout
                            fig.update_layout(
                                title=f"Floor {selected_floor} Plan",
                                autosize=True,
                                height=700,
                                xaxis=dict(
                                    scaleanchor="y",
                                    scaleratio=1,
                                    showgrid=False
                                ),
                                yaxis=dict(
                                    showgrid=False
                                ),
                                margin=dict(l=0, r=0, b=0, t=40),
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1
                                )
                            )
                            
                            # Display the plot
                            plotly(fig)
                            
                        elif view_type == "Single Apartment":
                            # Sample apartments if more than 10
                            if len(unique_apartments) > 10:
                                sample_apts = random.sample(unique_apartments, 10)
                                sample_apts.sort()
                            else:
                                sample_apts = sorted(unique_apartments)
                            
                            # Create apartment selection box
                            selected_apt = selectbox("Select an apartment:", options=sample_apts)
                            
                            if selected_apt:
                                # Filter data for selected apartment
                                apt_data = floor_data[floor_data['apartment_id'] == selected_apt]
                                text(f"### Apartment {selected_apt}")
                                text(f"Total elements: {len(apt_data)}")
                                
                                # Add legend toggle
                                show_legend = checkbox("Show entity type legend", default=False)
                                
                                # Create apartment plan
                                fig = go.Figure()
                                
                                # Process each geometry and add to the plot
                                for _, row in apt_data.iterrows():
                                    try:
                                        # Parse WKT geometry
                                        geom = shapely.wkt.loads(row['geometry'])
                                        
                                        # Get x, y coordinates (handling both Polygon and LineString types)
                                        if geom.geom_type == 'Polygon':
                                            x, y = zip(*geom.exterior.coords)
                                        elif geom.geom_type == 'LineString':
                                            x, y = zip(*geom.coords)
                                        else:
                                            # Skip other geometry types
                                            continue
                                        
                                        # Get color based on entity type
                                        color = colors.get(row['entity_type'], 'rgba(180, 180, 180, 0.5)')
                                        
                                        # Add shape to plot
                                        if geom.geom_type == 'Polygon':
                                            fig.add_trace(go.Scatter(
                                                x=x, y=y,
                                                fill='toself',
                                                fillcolor=color,
                                                line=dict(color='rgba(50, 50, 50, 0.8)', width=1),
                                                name=f"{row['entity_type']} - {row['entity_subtype']}",
                                                showlegend=show_legend
                                            ))
                                        else:  # LineString
                                            fig.add_trace(go.Scatter(
                                                x=x, y=y,
                                                mode='lines',
                                                line=dict(color=color, width=2),
                                                name=f"{row['entity_type']} - {row['entity_subtype']}",
                                                showlegend=show_legend
                                            ))
                                    except Exception as e:
                                        # Skip invalid geometries
                                        continue
                                
                                # Update layout
                                fig.update_layout(
                                    title=f"Apartment {selected_apt} Plan",
                                    autosize=True,
                                    height=600,
                                    xaxis=dict(
                                        scaleanchor="y",
                                        scaleratio=1,
                                        showgrid=False
                                    ),
                                    yaxis=dict(
                                        showgrid=False
                                    ),
                                    margin=dict(l=0, r=0, b=0, t=40),
                                    legend=dict(
                                        orientation="h",
                                        yanchor="bottom",
                                        y=1.02,
                                        xanchor="right",
                                        x=1
                                    )
                                )
                                
                                # Display the plot
                                plotly(fig)