from preswald import text, plotly, connect, get_df, table, selectbox, button, text_input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import numpy as np
import requests
import json

text("# Manoj Assessment")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('pokemon_data')


#Table Listing

#filter fields for table display and rename columns
df_table_display = df[['name', 'japanese_name', 'type1', 'type2','classfication' ,'generation','is_legendary']].copy()

# Rename 'is_legendary' to 'Legendary' and convert 0/1 to No/Yes
df_table_display['Legendary'] = df_table_display['is_legendary'].map({0: 'No', 1: 'Yes', False: 'No', True: 'Yes'})
df_table_display = df_table_display.drop('is_legendary', axis=1)


# Add "Any" option to the type lists
primary_types = ["Any"] + df["type1"].unique().tolist()
secondary_types = ["Any"] + df["type2"].unique().tolist()

# Create selectboxes with "Any" option
primary_type = selectbox("Primary Type", primary_types, default="Any", size=0.5)
secondary_type = selectbox("Secondary Type", secondary_types, default="Any", size=0.5)


# Filter by primary type if selected and not "Any"
if primary_type and primary_type != "Any":
    df_table_display = df_table_display[df_table_display['type1'] == primary_type]

# Filter by secondary type if selected and not "Any"
if secondary_type and secondary_type != "Any":
    df_table_display = df_table_display[df_table_display['type2'] == secondary_type]

table(df_table_display,title="Pokemon Data")


# Data Visualization Section
text("## Data Visualization")

# Define available plot types
plot_types = ["Scatter", "Histogram", "Bar Chart", "Box Plot", "Violin Plot", 
              "Density Contour", "Heatmap", "Bubble Chart", "Radar Chart", "3D Scatter"]

# Define available fields for plotting
numeric_fields = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed', 'base_total', 
                  'height_m', 'weight_kg', 'generation', 'pokedex_number']
categorical_fields = ['type1', 'type2', 'is_legendary', 'generation']
all_fields = numeric_fields + [f for f in categorical_fields if f not in numeric_fields]

# Plot selection
selected_plot_type = selectbox("Select Plot Type", plot_types)

# Based on plot type, show appropriate field selection options
if selected_plot_type in ["Scatter", "Bubble Chart", "3D Scatter", "Heatmap"]:
    # These plots need X and Y axes
    x_axis = selectbox("X-Axis", numeric_fields, default="attack", size=0.33)
    y_axis = selectbox("Y-Axis", numeric_fields, default="defense", size=0.33)
    
    # For plots that can use a color dimension
    color_by = selectbox("Color By", ["None"] + all_fields, default="type1", size=0.33)
    
    # For 3D scatter or bubble charts
    if selected_plot_type in ["3D Scatter", "Bubble Chart"]:
        z_axis = selectbox("Z-Axis/Size", numeric_fields, default="hp")
    
    # Filter option
    filter_by_type = selectbox("Filter by Type", ["All"] + df["type1"].unique().tolist(), default="All")
    
    # Create the plot based on selection
    if filter_by_type != "All":
        plot_df = df[df['type1'] == filter_by_type]
    else:
        plot_df = df
    
    if selected_plot_type == "Scatter":
        text(f"### Scatter Plot: {x_axis} vs {y_axis}")
        color_param = color_by if color_by != "None" else None
        fig = px.scatter(plot_df, x=x_axis, y=y_axis, color=color_param, 
                        hover_name="name",
                        title=f"{y_axis} vs {x_axis} by Pokemon",
                        labels={x_axis: x_axis.replace('_', ' ').title(), 
                                y_axis: y_axis.replace('_', ' ').title()})
        plotly(fig)
    
    elif selected_plot_type == "Bubble Chart":
        text(f"### Bubble Chart: {x_axis} vs {y_axis} (Size: {z_axis})")
        color_param = color_by if color_by != "None" else None
        fig = px.scatter(plot_df, x=x_axis, y=y_axis, size=z_axis, color=color_param,
                        hover_name="name", size_max=30,
                        title=f"{y_axis} vs {x_axis} (Bubble Size: {z_axis})",
                        labels={x_axis: x_axis.replace('_', ' ').title(), 
                                y_axis: y_axis.replace('_', ' ').title(),
                                z_axis: z_axis.replace('_', ' ').title()})
        plotly(fig)
    
    elif selected_plot_type == "3D Scatter":
        text(f"### 3D Scatter Plot: {x_axis} vs {y_axis} vs {z_axis}")
        color_param = color_by if color_by != "None" else None
        fig = px.scatter_3d(plot_df, x=x_axis, y=y_axis, z=z_axis, color=color_param,
                           hover_name="name",
                           title=f"3D Plot of {x_axis}, {y_axis}, and {z_axis}",
                           labels={x_axis: x_axis.replace('_', ' ').title(), 
                                   y_axis: y_axis.replace('_', ' ').title(),
                                   z_axis: z_axis.replace('_', ' ').title()})
        plotly(fig)
    
    elif selected_plot_type == "Heatmap":
        text(f"### Heatmap: {x_axis} vs {y_axis}")
        # For heatmap, we need to aggregate data
        if color_by != "None" and color_by in categorical_fields:
            # Use a pivot table for categorical color variable
            pivot_df = plot_df.pivot_table(index=y_axis, columns=x_axis, 
                                         values=color_by, aggfunc='count')
            title = f"Heatmap of Pokemon Count by {x_axis} and {y_axis}"
        else:
            # Use correlation for numeric variables
            corr_cols = [col for col in numeric_fields if col in plot_df.columns]
            pivot_df = plot_df[corr_cols].corr()
            title = "Correlation Heatmap of Pokemon Stats"
        
        fig = px.imshow(pivot_df, title=title, 
                       labels=dict(x=x_axis.replace('_', ' ').title(), 
                                  y=y_axis.replace('_', ' ').title(), 
                                  color="Value"))
        plotly(fig)

elif selected_plot_type in ["Histogram", "Box Plot", "Violin Plot"]:
    # These plots primarily need one field
    main_field = selectbox("Field", numeric_fields, default="base_total", size=0.5)
    group_by = selectbox("Group By", ["None"] + categorical_fields, default="type1", size=0.5)
    
    # Create the plot
    if selected_plot_type == "Histogram":
        text(f"### Histogram of {main_field}")
        if group_by != "None":
            fig = px.histogram(df, x=main_field, color=group_by, 
                              marginal="box", # include a box plot in the margin
                              barmode="overlay", # "overlay" or "stack"
                              histnorm="percent", # normalized to percentage
                              title=f"Distribution of {main_field} by {group_by}",
                              labels={main_field: main_field.replace('_', ' ').title()})
        else:
            fig = px.histogram(df, x=main_field,
                              marginal="box",
                              title=f"Distribution of {main_field}",
                              labels={main_field: main_field.replace('_', ' ').title()})
        plotly(fig)
    
    elif selected_plot_type == "Box Plot":
        text(f"### Box Plot of {main_field}")
        if group_by != "None":
            fig = px.box(df, x=group_by, y=main_field, color=group_by,
                        notched=True, # add notches to the boxes
                        title=f"Distribution of {main_field} by {group_by}",
                        labels={main_field: main_field.replace('_', ' ').title(),
                                group_by: group_by.replace('_', ' ').title()})
        else:
            fig = px.box(df, y=main_field,
                        title=f"Distribution of {main_field}",
                        labels={main_field: main_field.replace('_', ' ').title()})
        plotly(fig)
    
    elif selected_plot_type == "Violin Plot":
        text(f"### Violin Plot of {main_field}")
        if group_by != "None":
            fig = px.violin(df, x=group_by, y=main_field, color=group_by,
                           box=True, # include box plot inside the violin
                           points="all", # show all points
                           title=f"Distribution of {main_field} by {group_by}",
                           labels={main_field: main_field.replace('_', ' ').title(),
                                   group_by: group_by.replace('_', ' ').title()})
        else:
            fig = px.violin(df, y=main_field,
                           box=True,
                           points="all",
                           title=f"Distribution of {main_field}",
                           labels={main_field: main_field.replace('_', ' ').title()})
        plotly(fig)

elif selected_plot_type == "Bar Chart":
    # Bar charts work well with categorical data
    category = selectbox("Category", categorical_fields, default="type1", size=0.33)
    value = selectbox("Value", ["Count"] + numeric_fields, default="Count", size=0.33)
    sort_by = selectbox("Sort By", ["Alphabetical", "Value"], default="Value", size=0.33)
    
    text(f"### Bar Chart of {category}")
    
    if value == "Count":
        # Count the occurrences of each category
        count_df = df[category].value_counts().reset_index()
        count_df.columns = [category, 'Count']
        
        # Sort if requested
        if sort_by == "Value":
            count_df = count_df.sort_values('Count', ascending=False)
        else:
            count_df = count_df.sort_values(category)
        
        fig = px.bar(count_df, x=category, y='Count', color=category,
                    title=f"Count of Pokemon by {category}",
                    labels={category: category.replace('_', ' ').title(), 
                            'Count': 'Number of Pokemon'})
    else:
        # Aggregate the value by category
        agg_df = df.groupby(category)[value].mean().reset_index()
        
        # Sort if requested
        if sort_by == "Value":
            agg_df = agg_df.sort_values(value, ascending=False)
        else:
            agg_df = agg_df.sort_values(category)
        
        fig = px.bar(agg_df, x=category, y=value, color=category,
                    title=f"Average {value} by {category}",
                    labels={category: category.replace('_', ' ').title(),
                            value: value.replace('_', ' ').title()})
        plotly(fig)

elif selected_plot_type == "Density Contour":
    # Density contours work well with two numeric fields
    x_axis = selectbox("X-Axis", numeric_fields, default="attack", size=0.33)
    y_axis = selectbox("Y-Axis", numeric_fields, default="defense", size=0.33)
    group_by = selectbox("Group By", ["None"] + categorical_fields, default="type1", size=0.33)
    
    text(f"### Density Contour: {x_axis} vs {y_axis}")
    
    if group_by != "None":
        fig = px.density_contour(df, x=x_axis, y=y_axis, color=group_by,
                                marginal_x="histogram", marginal_y="histogram",
                                title=f"Density Contour of {y_axis} vs {x_axis} by {group_by}",
                                labels={x_axis: x_axis.replace('_', ' ').title(),
                                        y_axis: y_axis.replace('_', ' ').title()})
    else:
        fig = px.density_contour(df, x=x_axis, y=y_axis,
                                marginal_x="histogram", marginal_y="histogram",
                                title=f"Density Contour of {y_axis} vs {x_axis}",
                                labels={x_axis: x_axis.replace('_', ' ').title(),
                                        y_axis: y_axis.replace('_', ' ').title()})
    plotly(fig)

elif selected_plot_type == "Radar Chart":
    # Radar charts work well for comparing multiple dimensions
    text("### Radar Chart of Pokemon Stats")
    
    # Select Pokemon types to compare
    types_to_compare = [
        selectbox("Type 1", ["None"] + df["type1"].unique().tolist(), default="water", size=0.25),
        selectbox("Type 2", ["None"] + df["type1"].unique().tolist(), default="fire", size=0.25),
        selectbox("Type 3", ["None"] + df["type1"].unique().tolist(), default="grass", size=0.25),
        selectbox("Type 4", ["None"] + df["type1"].unique().tolist(), default="electric", size=0.25)
    ]
    types_to_compare = [t for t in types_to_compare if t != "None"]
    
    if types_to_compare:
        # Calculate average stats for each selected type
        stats_cols = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
        radar_data = []
        
        for poke_type in types_to_compare:
            type_stats = df[df['type1'] == poke_type][stats_cols].mean().to_dict()
            type_stats['type'] = poke_type
            radar_data.append(type_stats)
        
        radar_df = pd.DataFrame(radar_data)
        
        # Convert to long form for plotting
        radar_long = pd.melt(radar_df, id_vars=['type'], value_vars=stats_cols,
                           var_name='stat', value_name='value')
        
        fig = px.line_polar(radar_long, r='value', theta='stat', color='type', line_close=True,
                           title='Comparison of Average Stats by Pokemon Type',
                           labels={'value': 'Stat Value', 'stat': 'Stat', 'type': 'Pokemon Type'})
        plotly(fig)
    else:
        text("Please select at least one Pokemon type to display the radar chart.")


# Pokemon Type Effectiveness Network Section
text("## Pokemon Type Effectiveness Network")
text("Enter a Pokemon name to see its type effectiveness relationships:")

# Text input for Pokemon name
pokemon_name = text_input("Pokemon Name", placeholder="e.g. Pikachu")

if pokemon_name:
    # Check if the Pokemon exists in the dataset
    if pokemon_name.lower() in df['name'].str.lower().values:
        # Get the Pokemon's details
        pokemon_data = df[df['name'].str.lower() == pokemon_name.lower()].iloc[0]
        primary_type = pokemon_data['type1']
        secondary_type = pokemon_data['type2'] if not pd.isna(pokemon_data['type2']) else None
        
        # Fetch Pokemon sprite from PokeAPI
        try:
            # Make API request to PokeAPI
            api_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                pokemon_api_data = response.json()
                sprite_url = pokemon_api_data['sprites']['front_default']
                
                # Display Pokemon sprite using Plotly
                if sprite_url:
                    # Create a simple figure for the sprite
                    sprite_fig = go.Figure()
                    
                    # Add image to the center of the figure
                    sprite_fig.add_layout_image(
                        dict(
                            source=sprite_url,
                            xref="paper", yref="paper",
                            x=0.5, y=0.5,
                            sizex=0.8, sizey=0.8,
                            xanchor="center", yanchor="middle"
                        )
                    )
                    
                    # Configure layout to make image larger and remove all axes elements
                    sprite_fig.update_layout(
                        width=400,
                        height=400,
                        margin=dict(l=0, r=0, t=0, b=0),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(
                            showgrid=False,
                            zeroline=False,
                            showticklabels=False,
                            visible=False
                        ),
                        yaxis=dict(
                            showgrid=False,
                            zeroline=False,
                            showticklabels=False,
                            visible=False
                        )
                    )
                    
                    text(f"## {pokemon_data['name'].title()}")
                    plotly(sprite_fig)
            else:
                text(f"Could not fetch sprite for {pokemon_name} from PokeAPI (Status code: {response.status_code})")
                
        except Exception as e:
            text(f"Error fetching Pokemon sprite: {str(e)}")
        
        text(f"Type Effectiveness Network for {pokemon_data['name']}")
        
        # Define all Pokemon types
        all_types = sorted(df['type1'].unique())
        
        # Get the defensive effectiveness data from the dataset
        effectiveness_columns = [col for col in df.columns if col.startswith('against_')]
        
        # Get the actual effectiveness multipliers for each type against this Pokemon
        effectiveness_data = {}
        for col in effectiveness_columns:
            # Extract the type name from column name (against_fire -> fire)
            attack_type = col.replace('against_', '')
            effectiveness_data[attack_type] = pokemon_data[col]
        
        # Define node colors for different types (using Pokemon-like colors)
        type_colors = {
            'normal': '#A8A878', 'fire': '#F08030', 'water': '#6890F0',
            'electric': '#F8D030', 'grass': '#78C850', 'ice': '#98D8D8',
            'fighting': '#C03028', 'poison': '#A040A0', 'ground': '#E0C068',
            'flying': '#A890F0', 'psychic': '#F85888', 'bug': '#A8B820',
            'rock': '#B8A038', 'ghost': '#705898', 'dragon': '#7038F8',
            'dark': '#705848', 'steel': '#B8B8D0', 'fairy': '#EE99AC'
        }
        
        # Map column names to correct type names if needed (e.g., 'fight' -> 'fighting')
        type_mapping = {
            'fight': 'fighting',
            # Add any other mappings if column names differ from actual type names
        }
        
        # Define effectiveness colors for different multipliers
        effectiveness_colors = {
            0: '#888888',     # Gray for Immunity (No Effect)
            0.25: '#00AA00',  # Darker Green for Doubly Resistant
            0.5: '#00FF00',   # Green for Resistant
            1: '#AAAAAA',     # Light Gray for Neutral
            2: '#FF0000',     # Red for Super Effective
            4: '#CC0000'      # Darker Red for Doubly Super Effective
        }
        
        # Create a network graph
        G = nx.Graph()
        
        # Add central node (the Pokemon)
        G.add_node('pokemon', name=pokemon_data['name'])
        
        # Add type nodes
        G.add_node(primary_type)
        if secondary_type:
            G.add_node(secondary_type)
        
        # Add nodes for attacking types (filter out duplicates)
        types_to_include = []
        for attack_type, multiplier in effectiveness_data.items():
            # Map to correct type name if needed
            if attack_type in type_mapping:
                attack_type = type_mapping[attack_type]
            
            if attack_type not in [primary_type, secondary_type] and attack_type not in types_to_include:
                types_to_include.append(attack_type)
                G.add_node(attack_type)
        
        # Create positions for each node
        pos = {}
        
        # Position the Pokemon at the center
        pos['pokemon'] = (0, 0)
        
        # Position primary and secondary types near the Pokemon
        angle_offset = 0
        pos[primary_type] = (0.3 * np.cos(angle_offset), 0.3 * np.sin(angle_offset))
        if secondary_type:
            angle_offset = np.pi  # Opposite side from primary type
            pos[secondary_type] = (0.3 * np.cos(angle_offset), 0.3 * np.sin(angle_offset))
        
        # Position attacking types in a circle around the center
        n_attacking_types = len(types_to_include)
        radius = 1.0
        for i, attack_type in enumerate(types_to_include):
            angle = 2 * np.pi * i / n_attacking_types
            pos[attack_type] = (radius * np.cos(angle), radius * np.sin(angle))
        
        # Store positions in node attributes
        for node, position in pos.items():
            G.nodes[node]['pos'] = position
        
        # Create edges with effectiveness data
        # Group edges by effectiveness multiplier
        edges_by_effectiveness = {
            0: [],
            0.25: [],
            0.5: [],
            1: [],
            2: [],
            4: []
        }
        
        # Add edges from attacking types to Pokemon
        for attack_type, multiplier in effectiveness_data.items():
            # Map to correct type name if needed
            if attack_type in type_mapping:
                mapped_type = type_mapping[attack_type]
            else:
                mapped_type = attack_type
                
            # Skip if the attacking type node doesn't exist
            if mapped_type not in G.nodes():
                continue
                
            # Add edge with effectiveness data
            G.add_edge(mapped_type, 'pokemon', effectiveness=multiplier)
            
            # Store edge in appropriate group
            edges_by_effectiveness[multiplier].append((mapped_type, 'pokemon'))
        
        # Prepare edge traces by effectiveness multiplier
        edge_traces = {}
        
        for multiplier, color in effectiveness_colors.items():
            if multiplier == 0:
                label = "Immune (0×)"
            elif multiplier == 0.25:
                label = "Doubly Resistant (0.25×)"
            elif multiplier == 0.5:
                label = "Resistant (0.5×)"
            elif multiplier == 1:
                label = "Neutral (1×)"
            elif multiplier == 2:
                label = "Super Effective (2×)"
            else:  # multiplier == 4
                label = "Doubly Super Effective (4×)"
                
            edge_traces[multiplier] = go.Scatter(
                x=[], y=[],
                line=dict(width=3, color=color),
                hoverinfo='text',
                text=[],
                mode='lines',
                name=label
            )
        
        # Add edges to appropriate traces
        for multiplier, edges in edges_by_effectiveness.items():
            for source, target in edges:
                x0, y0 = pos[source]
                x1, y1 = pos[target]
                
                trace = edge_traces[multiplier]
                trace['x'] += (x0, x1, None)
                trace['y'] += (y0, y1, None)
                trace['text'] += (f"{source.title()} is {multiplier}× effective against {pokemon_data['name']}",)
        
        # Create node traces
        # Special trace for the Pokemon
        pokemon_trace = go.Scatter(
            x=[pos['pokemon'][0]],
            y=[pos['pokemon'][1]],
            text=[pokemon_data['name']],
            mode='markers+text',
            textposition='middle center',
            textfont=dict(family='Arial', size=14, color='white'),
            hoverinfo='text',
            marker=dict(
                color='#FF5733',  # Orange-red for the Pokemon
                size=70,  # Increased from 35
                line=dict(width=2, color='white')
            )
        )
        
        # Trace for type nodes
        type_node_trace = go.Scatter(
            x=[], y=[],
            text=[],
            mode='markers+text',
            textposition='middle center',
            textfont=dict(family='Arial', size=12, color='white'),
            hoverinfo='text',
            marker=dict(
                color=[],
                size=[],
                line=dict(width=2, color='white')
            )
        )
        
        # Add type nodes
        for node in G.nodes():
            if node == 'pokemon':
                continue  # Skip Pokemon node as it's in a separate trace
                
            x, y = pos[node]
            type_node_trace['x'] += (x,)
            type_node_trace['y'] += (y,)
            
            # Set node size - making them bigger
            size = 80 if node in [primary_type, secondary_type] else 60  # Increased from 30/20
            type_node_trace['marker']['size'] += (size,)
            
            # Set node color based on type
            color = type_colors.get(node, '#9966CC')
            type_node_trace['marker']['color'] += (color,)
            
            # Set node text
            type_node_trace['text'] += (node.title(),)
        
        # Create figure with all traces
        # First add edges by effectiveness (from least to most noticeable)
        data = []
        for multiplier in [1, 0.5, 0.25, 0, 2, 4]:
            if len(edge_traces[multiplier]['x']) > 0:
                data.append(edge_traces[multiplier])
        
        # Then add node traces
        data.append(type_node_trace)
        data.append(pokemon_trace)
        
        fig = go.Figure(
            data=data,
            layout=go.Layout(
                title=dict(
                    text=f"Defensive Type Effectiveness for {pokemon_data['name']}",
                    font=dict(size=26)
                ),
                showlegend=False,
                hovermode='closest',
                height=1200,
                width=1600,
                plot_bgcolor='rgba(240,240,240,0.8)',
                xaxis=dict(
                    visible=False,
                    range=[-1.5, 1.5],
                    fixedrange=True,
                    showgrid=False,  # Explicitly disable grid
                    zeroline=False,  # Remove zero line
                    showspikes=False
                ),
                yaxis=dict(
                    visible=False,
                    range=[-1.5, 1.5],
                    fixedrange=True,
                    showgrid=False,  # Explicitly disable grid
                    zeroline=False,  # Remove zero line
                    showspikes=False
                ),
                margin=dict(b=0, l=0, r=0, t=40),
                paper_bgcolor='rgba(0,0,0,0)',

            )
        )

        plotly(fig)
        
        
        
    else:
        text(f"Pokemon '{pokemon_name}' not found. Please check the spelling or try another Pokemon.")





