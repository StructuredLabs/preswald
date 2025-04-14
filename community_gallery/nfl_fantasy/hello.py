from preswald import text, plotly, connect, get_df, table, slider
import plotly.express as px

# Title
text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Connect and Load the Dataset
connect()

try:
    df = get_df("2024_player_predictions")  # Load the dataset
    
    if df is None:
        text("⚠️ Error: Dataset '2024_player_predictions' is None.")
        print("Error: df is None")
    elif df.empty:
        text("⚠️ Error: Dataset '2024_player_predictions' is empty.")
        print("Error: df is empty")
    else:
        # Print DataFrame preview in terminal
        print(df.head())
        print(df.columns)

        # Display the dataset
        table(df, title="Player Predictions Data")

        # Scatter Plot: Total Yards vs Fantasy Points (PPR)
        if 'total_yards' in df.columns and 'fantasy_points_ppr' in df.columns:
            fig = px.scatter(df, x='total_yards', y='fantasy_points_ppr', text='player_name',
                             title='Total Yards vs Fantasy Points (PPR)',
                             labels={'total_yards': 'Total Yards', 'fantasy_points_ppr': 'Fantasy Points (PPR)'})

            fig.update_traces(textposition='top center', marker=dict(size=10, color='blue'))
            fig.update_layout(template='plotly_white')

            plotly(fig)  # Show the plot
        else:
            text("⚠️ Error: Column names do not match. Check the dataset headers.")
            print("Error: Columns not found in dataset:", df.columns)

        # Add a slider for dynamic filtering
        threshold = slider("Minimum Fantasy Points (PPR)", min_val=0, max_val=500, default=80)
        if 'fantasy_points_ppr' in df.columns:
            filtered_df = df[df["fantasy_points_ppr"] > threshold]
            table(filtered_df, title="Filtered Players by Fantasy Points (PPR)")

except Exception as e:
    text(f"❌ Error loading dataset: {e}")
    print("Exception:", e)