# Import required libraries
from preswald import connect, text, table, slider, plotly
import pandas as pd
import plotly.express as px
import os

# Initialize connection to data sources
connect()

# Load the dataset from a local file instead of using get_df
try:
    # Check if the data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
        text("⚠️ Created data directory. Please place your CSV file there.")
    
    # List files in data directory
    data_files = os.listdir('data')
    
    if data_files:
        text(f"Found these files in data directory: {', '.join(data_files)}")
        
        # Try to load the first CSV file found
        csv_files = [f for f in data_files if f.endswith('.csv')]
        
        if csv_files:
            first_csv = csv_files[0]
            text(f"Loading dataset: {first_csv}")
            df = pd.read_csv(f"data/{first_csv}")
            
            # Display the raw data table
            text("## Raw Data")
            table(df, title=f"{first_csv} Dataset")
            
            # Get numeric columns for slider
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if numeric_cols:
                # Create an interactive filter with the first numeric column
                filter_col = numeric_cols[0]
                text(f"## Interactive Filter")
                min_val = float(df[filter_col].min())
                max_val = float(df[filter_col].max())
                default_val = min_val + (max_val - min_val) / 2
                
                filter_value = slider(f"Filter by {filter_col}", 
                                    min_val=min_val,
                                    max_val=max_val, 
                                    default=default_val)
                
                # Show filtered data
                filtered_df = df[df[filter_col] >= filter_value]
                table(filtered_df, title=f"Filtered Data (where {filter_col} >= {filter_value})")
                
                # Create a simple visualization if there are at least two numeric columns
                if len(numeric_cols) >= 2:
                    text("## Data Visualization")
                    
                    # Get categorical columns for coloring
                    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
                    color_col = categorical_cols[0] if categorical_cols else None
                    
                    fig = px.scatter(df, 
                                    x=numeric_cols[0], 
                                    y=numeric_cols[1], 
                                    color=color_col,
                                    title=f"{numeric_cols[0]} vs {numeric_cols[1]}")
                    plotly(fig)
                    
                    # Create another visualization if possible
                    if len(numeric_cols) >= 4:
                        fig2 = px.scatter(df, 
                                        x=numeric_cols[2], 
                                        y=numeric_cols[3], 
                                        color=color_col,
                                        title=f"{numeric_cols[2]} vs {numeric_cols[3]}")
                        plotly(fig2)
            else:
                text("⚠️ No numeric columns found in the dataset for filtering or visualization.")
        else:
            text("⚠️ No CSV files found in the data directory. Please add a CSV file to the data folder.")
    else:
        text("⚠️ No files found in the data directory. Please add a CSV file to the data folder.")
        
except Exception as e:
    text(f"# Error")
    text(f"An error occurred: {str(e)}")
    text("## Troubleshooting")
    text("1. Make sure you have a CSV file in the 'data' folder")
    text("2. Make sure the CSV file has the expected format")
    text("3. If you haven't downloaded a dataset yet, follow these steps:")
    text("   - Download a CSV dataset from Kaggle or another source")
    text("   - Place it in the 'data' folder of your project")
    text("   - Restart the app")