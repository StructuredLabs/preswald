from preswald import connect, get_df, table, text, plotly, slider, selectbox, separator, alert, checkbox
import plotly.express as px

# Connect to Preswald data sources
connect()
df = get_df("sales_data")  # Load dataset

# Display title
text("# Sales Data Analysis App")

# Check if df is None before proceeding
if df is None:
    alert("Error: Dataset 'sales_data' not found. Ensure it is correctly configured in preswald.toml.", type="error")
else:
    # Debugging: Print available columns
    # table(df.head())
    text(f"Columns in dataset: {', '.join(df.columns)}")

    # Ensure DataFrame is loaded and contains required columns
    if not df.empty and all(col in df.columns for col in ['Quantity_Sold', 'Sales_Amount', 'Product_ID', 'Product_Category']):

        separator()  # Add visual break

        # Add slider to control number of rows displayed
        num_rows = slider("Select number of rows to display", min_val=5, max_val=50, step=5, default=10)
        table(df.head(num_rows))

        separator()  # Add another visual break

        # Add selectbox for column selection
        column_choice = selectbox("Choose a column to visualize", options=['Quantity_Sold', 'Sales_Amount'])
        
        # Display histogram based on selected column
        fig_hist = px.histogram(df, x=column_choice, title=f"Distribution of {column_choice}")
        plotly(fig_hist)

        separator()  # Add another visual break

        # Add checkbox for toggling between full dataset and filtered dataset
        show_filtered = checkbox("Show only high sales data (Sales Amount > 5000)")

        if show_filtered:
            df_filtered = df[df['Sales_Amount'] > 5000]
            table(df_filtered.head(num_rows))
        else:
            table(df.head(num_rows))

        # Create scatter plot with hover labels (removing static text labels)
        fig = px.scatter(df, x='Quantity_Sold', y='Sales_Amount', hover_name='Product_ID',
                         color='Product_Category',
                         title='Quantity Sold vs. Sales Amount',
                         labels={'Quantity_Sold': 'Quantity Sold', 'Sales_Amount': 'Sales Amount'})

        # Update traces for better readability
        fig.update_traces(marker=dict(size=6, opacity=0.6))

        # Style the plot
        fig.update_layout(template='plotly_white')

        # Show the plot
        plotly(fig)

    else:
        alert("Error: Data failed to load or missing required columns. Please check the dataset.", type="error")
