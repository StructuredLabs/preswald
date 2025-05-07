from preswald import text, plotly, table, slider
import pandas as pd
import plotly.express as px

# Display initial texts
text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Attempt to load the CSV directly using pandas
file_path = 'FIFA21Complete.csv'  # Path to the CSV file

try:
    # Load the CSV data into a DataFrame
    df = pd.read_csv(file_path, delimiter=';')

    # Check if the DataFrame has been loaded successfully
    if df is not None:
        # Display information about the loaded data
        text(f"Dataset loaded successfully! Number of rows: {len(df)}")
        text(f"Columns: {', '.join(df.columns)}")

        # Show the first few rows of the dataset
        text(f"First few rows of the dataset:\n{df.head()}")

        # Create a scatter plot if necessary columns exist
        if all(col in df.columns for col in ['hits', 'potential', 'name']):
            fig = px.scatter(df, x='hits', y='potential', text='name',
                             title='Hits vs Potential',
                             labels={'hits': 'Hits', 'potential': 'Potential'})
            
            # Style the plot
            fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))
            fig.update_layout(template='plotly_white')

            # Show the plot
            plotly(fig)

            # Show the data in a table
            table(df)

            # Add a dynamic slider to filter data based on the 'hits' column
            threshold = slider("Threshold", min_val=0, max_val=300, default=50)  # Adjust slider range to match the 'hits' range
            filtered_df = df[df["hits"] > threshold]  # Filtering based on 'hits' column
            table(filtered_df, title="Dynamic Data View")
        else:
            text("The dataset does not have the required columns: 'hits', 'potential', 'name'. Please check the data.")
    else:
        text("Failed to load the dataset. Please check the file path or format.")

except Exception as e:
    text(f"Error: {e}")