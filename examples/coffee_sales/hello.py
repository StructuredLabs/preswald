from preswald import text, plotly, connect, get_df, table, slider, query
import plotly.express as px
import pandas as pd




# Title and Introduction
text("# Sales Dashboard ☕️")
text("Explore sales trends, product performance, and discount impacts.")

# Load the CSV dataset
connect()  # Load data sources
df = get_df('coffee_csv')

# Add a slider to filter by minimum sales amount
sales_threshold = slider("Minimum Sales Amount", min_val=500, max_val=2000, default=500, step=50)

# Query: Select sales above the threshold
sql_query = f"""
SELECT * FROM coffee_csv
WHERE Sales_Amount >= {sales_threshold}
"""
filtered_df = query(sql_query, "coffee_csv")

# Debugging: Print the query and DataFrame
#text(sql_query)
#text(filtered_df)

# Handle NoneType or empty DataFrame
if filtered_df is None:
    text("No data available or error in query execution.")
elif filtered_df.empty:
    text("No data available for the selected criteria.")
else:
    # 1. Bar plot for Sales by City and Product
    sales_by_city_product = filtered_df.groupby(["City", "Product"])["Quantity"].sum().reset_index()
    fig = px.bar(
        sales_by_city_product, x='City', y='Quantity', color='Product',
        title='Units Sold by City and Product',
        labels={'Quantity': 'Units Sold', 'City': 'City', 'Product': 'Product'}
    )

    # Customize plot appearance
    fig.update_layout(template='plotly_white', barmode='stack')

    # Show the bar plot
    plotly(fig)

    # 2. Average Sales by Product
    avg_sales_df = filtered_df.groupby("Product")["Final_Sales"].mean().reset_index()
    fig2 = px.bar(avg_sales_df, x="Product", y="Final_Sales", title="Average Sales by Product")
    plotly(fig2)

      # 3. Sales Amount Scatter Plot
    fig3 = px.scatter(filtered_df, x="Final_Sales", y="Quantity", color="Product", title="Final Sales Amount vs Quantity")
    plotly(fig3)

    # 4. Bar Plot for Sales by City
    city_sales_df = filtered_df.groupby("City")["Final_Sales"].sum().reset_index()
    fig4 = px.bar(city_sales_df, x="City", y="Final_Sales", title="Total Sales by City")
    plotly(fig4)
   

    # Show the filtered data in a table
    table(filtered_df, title="High Sales Records")
