from preswald import text, table, slider, connect, get_df, plotly
import plotly.express as px

text("# **Welcome to the Electric Vehicle Data Explorer!**")
text("Explore key stats about electric vehicles. Use the slider to filter by Model Year, and see each vehicle's make on the chart.")

connect()
df = get_df("ev")  

if df is None:
    text("Error: EV data did not load. Check your CSV file and preswald.toml.")
else:
    # Summary statistics
    total_vehicles = len(df)
    avg_range = df["Electric Range"].mean() if "Electric Range" in df.columns else 0
    text(f"**Total Vehicles:** {total_vehicles}")
    text(f"**Average Electric Range:** {avg_range:.2f} miles")
    
    # Check for Model Year column to set up the slider
    if "Model Year" in df.columns:
        min_year = int(df["Model Year"].min())
        max_year = int(df["Model Year"].max())
        
        # Slider to filter vehicles by model year
        chosen_year = slider(
            "Filter vehicles by Model Year (show vehicles produced from this year onward):",
            min_val=min_year,
            max_val=max_year,
            default=min_year
        )
        
        # Filter the data based on the chosen year
        filtered_df = df[df["Model Year"] >= chosen_year]
        text(f"Showing vehicles produced from **{chosen_year}** onward:")

        # Create a scatter plot with Make labels on each data point
        if "Electric Range" in filtered_df.columns and "Make" in filtered_df.columns:
            fig = px.scatter(
                filtered_df,
                x="Model Year",
                y="Electric Range",
                color="Make",
                title="Electric Range by Model Year",
                labels={"Model Year": "Model Year", "Electric Range": "Electric Range"},
                hover_data=["Make", "Model Year", "Electric Range"]
            )
            fig.update_traces(textposition='top center', marker=dict(size=12))
            fig.update_layout(template='plotly_white')
            plotly(fig)
        else:
            text("Error: Required columns for plot ('Electric Range' and 'Make') not found.")

        table(filtered_df)
    else:
        text("Error: 'Model Year' column not found in the data.")
