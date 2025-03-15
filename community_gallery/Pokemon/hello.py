from preswald import text, plotly, connect, get_df, table,selectbox,button
import pandas as pd
import plotly.express as px

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
categorical_fields = ['type1', 'type2', 'is_legendary', 'generation', 'classfication']
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



