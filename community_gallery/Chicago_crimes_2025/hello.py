import plotly.express as px
import pandas as pd
from preswald import connect, get_df, plotly, query, slider, table, text, selectbox, text_input, checkbox, separator

# Display title and introduction
text("# Chicago Crime Dashboard 2025")
text("### Explore crime data across Chicago neighborhoods")

# Load the dataset with error handling
try:
    connect()  # Initialize connection
    # Using the exact filename from your document
    df = get_df("sample_csv")
    
    if df is None or len(df) == 0:
        text("⚠️ Dataset appears to be empty or not properly loaded.")
    else:
        text(f"✅ Successfully loaded Chicago Crime dataset with {len(df)} records.")
        
        # Display basic information about the dataset
        text("## Dataset Overview")
        table(df.head(), title="Sample of Crime Records")
        
        # Crime Types Analysis
        text("## Crime Type Analysis")
        
        if "Primary Type" in df.columns:
            # Get crime counts by type
            crime_by_type = df["Primary Type"].value_counts().reset_index()
            crime_by_type.columns = ["Crime Type", "Count"]
            
            # Create visualization
            fig1 = px.bar(
                crime_by_type.head(10),
                x="Crime Type",
                y="Count",
                title="Most Common Crime Types",
                color="Crime Type"
            )
            plotly(fig1)
            
            # Allow selecting specific crime type
            crime_types = ["All"] + sorted(df["Primary Type"].unique().tolist())
            selected_crime = selectbox("Select Crime Type to Analyze", options=crime_types)
            
            if selected_crime != "All":
                # Filter for selected crime
                filtered_crimes = df[df["Primary Type"] == selected_crime]
                text(f"Showing {len(filtered_crimes)} incidents of {selected_crime}")
                
                # Show locations for this crime type
                if "Location Description" in df.columns:
                    crime_locations = filtered_crimes["Location Description"].value_counts().reset_index()
                    crime_locations.columns = ["Location", "Count"]
                    
                    fig2 = px.pie(
                        crime_locations.head(8),
                        values="Count",
                        names="Location",
                        title=f"Where {selected_crime} Occurs Most Often"
                    )
                    plotly(fig2)
            
        separator()
        
        # Arrest Analysis
        text("## Arrest Analysis")
        
        if "Arrest" in df.columns:
            # Calculate arrest rates
            arrest_counts = df["Arrest"].value_counts()
            total_crimes = len(df)
            
            arrest_data = [
                {"Status": "Arrested", "Count": int(arrest_counts.get(True, 0))},
                {"Status": "Not Arrested", "Count": int(arrest_counts.get(False, 0))}
            ]
            
            fig3 = px.pie(
                arrest_data,
                values="Count",
                names="Status",
                title="Arrest vs. Non-Arrest Cases",
                color="Status",
                color_discrete_map={"Arrested": "green", "Not Arrested": "red"}
            )
            plotly(fig3)
            
            # Show arrest rates by crime type
            crime_arrest_rates = df.groupby("Primary Type").agg(
                total=("ID", "count"),
                arrested=("Arrest", lambda x: sum(x == True))
            ).reset_index()
            
            crime_arrest_rates["arrest_rate"] = (crime_arrest_rates["arrested"] / crime_arrest_rates["total"] * 100).round(1)
            crime_arrest_rates = crime_arrest_rates.sort_values("arrest_rate", ascending=False)
            
            fig4 = px.bar(
                crime_arrest_rates.head(10),
                x="Primary Type",
                y="arrest_rate",
                title="Crime Types with Highest Arrest Rates (%)",
                labels={"Primary Type": "Crime Type", "arrest_rate": "Arrest Rate (%)"}
            )
            plotly(fig4)
        
        separator()
        
        # Location Analysis
        text("## Location Analysis")
        
        if "Location Description" in df.columns:
            top_locations = df["Location Description"].value_counts().reset_index()
            top_locations.columns = ["Location", "Count"]
            
            fig5 = px.bar(
                top_locations.head(10),
                x="Location",
                y="Count",
                title="Most Common Crime Locations",
                color="Location"
            )
            plotly(fig5)
            
            # Select location for detailed analysis
            locations = ["All"] + sorted(top_locations["Location"].head(20).tolist())
            selected_location = selectbox("Select a Location for Detailed Analysis", options=locations)
            
            if selected_location != "All":
                location_crimes = df[df["Location Description"] == selected_location]
                
                # Show crime types at this location
                location_crime_types = location_crimes["Primary Type"].value_counts().reset_index()
                location_crime_types.columns = ["Crime Type", "Count"]
                
                fig6 = px.pie(
                    location_crime_types.head(8),
                    values="Count",
                    names="Crime Type",
                    title=f"Types of Crimes at {selected_location}"
                )
                plotly(fig6)
        
        separator()
        
        # Geographic Analysis (if coordinates are available)
        text("## Geographic Analysis")
        
        if all(col in df.columns for col in ["Latitude", "Longitude"]):
            # Filter out invalid coordinates
            geo_data = df.dropna(subset=["Latitude", "Longitude"])
            
            # Check if we have valid numeric data
            if len(geo_data) > 0 and pd.to_numeric(geo_data["Latitude"], errors="coerce").notna().any():
                # Limit to sample for performance
                map_sample = geo_data.sample(min(1000, len(geo_data)))
                
                fig7 = px.scatter_mapbox(
                    map_sample,
                    lat="Latitude",
                    lon="Longitude",
                    color="Primary Type",
                    hover_name="Primary Type",
                    hover_data=["Description", "Location Description"],
                    zoom=10,
                    title="Crime Map of Chicago"
                )
                fig7.update_layout(mapbox_style="open-street-map")
                plotly(fig7)
            else:
                text("⚠️ Geographic data doesn't contain valid coordinates for mapping.")
        
        separator()
        
        # Search functionality
        text("## Search Crime Records")
        
        search_term = text_input("Enter search term (e.g., robbery, domestic):")
        
        if search_term:
            # Search across relevant text columns
            search_columns = [col for col in ["Primary Type", "Description", "Location Description", "Block"] 
                             if col in df.columns]
            
            # Build search mask
            mask = pd.Series(False, index=df.index)
            for col in search_columns:
                mask = mask | df[col].astype(str).str.contains(search_term, case=False, na=False)
            
            # Show results
            search_results = df[mask]
            text(f"Found {len(search_results)} records matching '{search_term}'")
            
            if len(search_results) > 0:
                # Display results table
                display_columns = [col for col in ["Date", "Primary Type", "Description", 
                                                 "Location Description", "Arrest", "District"]
                                  if col in df.columns]
                table(search_results[display_columns].head(20), 
                      title=f"Search Results for '{search_term}'")
            else:
                text("No matching records found.")
        
except Exception as e:
    text(f"⚠️ Error while working with the dataset: {str(e)}")
    text("Please check if the dataset is correctly loaded and has the expected format.")