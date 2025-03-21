from preswald import connect, get_df, query, table, text, slider, selectbox, alert, checkbox, plotly
import pandas as pd
import plotly.express as px

connect()

text("# Big-4-financial-risk 📊")
text("Welcome to the Big-4-financial-risk Explorer! This interactive app helps you analyze financial risk metrics for major accounting firms.")

# Load the dataset
df = get_df("big4_financial_risk_compliance")

if df is None or df.empty:
    alert("⚠️ No data found. Please check that your dataset is available in the data/ folder.")
else:
    alert("✅ Dataset loaded successfully!")
    
    # Display dataset overview
    text("## Dataset Overview")
    table(df.head(5), title="Sample Data")
    
    # User controls for data filtering
    text("## Data Filtering")
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    
    if numeric_columns:
        # Let user select which metric to analyze
        selected_numeric = selectbox("Select Financial Metric to Filter By", options=numeric_columns)
        
        # Create slider for threshold selection
        threshold = slider(
            f"Set threshold value for {selected_numeric}",
            min_val=float(df[selected_numeric].min()),
            max_val=float(df[selected_numeric].max()),
            default=float(df[selected_numeric].median())
        )
        
        # Filter data based on user selection
        filtered_df = df[df[selected_numeric] > threshold]
        
        # Display filtered results
        text(f"## Filtered Results ({len(filtered_df)} records)")
        table(filtered_df, title=f"Entries with {selected_numeric} > {threshold}")
    else:
        alert("⚠️ No numeric columns available for analysis.")
    
    # SQL query section
    if numeric_columns:
        text("## SQL Analysis")
        try:
            sql = f"""
            SELECT * 
            FROM big4_financial_risk_compliance 
            WHERE "{selected_numeric}" > {threshold}
            LIMIT 10
            """
            query_df = query(sql, "big4_financial_risk_compliance")
            table(query_df, title="SQL Query Results (Top 10 matches)")
        except Exception as e:
            alert(f"⚠️ SQL query failed: {str(e)}")
    
    # Data visualization section
    text("## Data Visualization")
    if len(numeric_columns) >= 2:
        # Let user select which metrics to plot
        x_axis = selectbox("Select X-axis Metric", options=numeric_columns)
        y_axis = selectbox("Select Y-axis Metric", options=numeric_columns)
        
        # Create the scatter plot
        text("### Relationship Analysis")
        fig = px.scatter(
            df,
            x=x_axis,
            y=y_axis,
            title=f"Correlation: {x_axis} vs {y_axis}",
            labels={x_axis: x_axis.replace("_", " ").title(), 
                   y_axis: y_axis.replace("_", " ").title()},
            opacity=0.7,
            color_discrete_sequence=["#1f77b4"]
        )
        fig.update_layout(
            plot_bgcolor='white',
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray')
        )
        plotly(fig)
        
        # Add correlation value calculation manually
        try:
            corr_value = df[[x_axis, y_axis]].corr().iloc[0,1]
            text(f"**Correlation coefficient: {corr_value:.2f}**")
        except:
            text("**Unable to calculate correlation coefficient**")
    else:
        alert("⚠️ Need at least two numeric columns for correlation analysis.")
    
    # Summary
    text("## Summary")
    text("This application provides basic analysis tools for exploring big-4-financial risks and identifying patterns.")