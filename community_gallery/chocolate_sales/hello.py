import pandas as pd
import plotly.express as px

from preswald import connect, get_df, plotly, slider, table, text

# Report Title
text(
    "# Chocolate Sales Analysis \n This report provides a visual analysis of chocolate sales data across different countries, products, and sales personnel."
)

# Load the CSV
connect()
chocolate_df = get_df("chocolate_sales_csv")

# Data preprocessing
# Convert Amount column to numeric by removing $ and commas
chocolate_df['Amount'] = chocolate_df['Amount'].str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip().astype(float)

# Convert Date to datetime format
chocolate_df['Date'] = pd.to_datetime(chocolate_df['Date'], format='%d-%b-%y')

# Add a month column for time analysis
chocolate_df['Month'] = chocolate_df['Date'].dt.month_name()

# Calculate average price per box
chocolate_df['Price Per Box'] = chocolate_df['Amount'] / chocolate_df['Boxes Shipped']

# Sales by Country
text(
    "## Sales by Country \n This bar chart shows the total sales amount by country."
)
country_sales = chocolate_df.groupby('Country')['Amount'].sum().reset_index()
fig1 = px.bar(
    country_sales,
    x='Country',
    y='Amount',
    title='Total Sales by Country',
    labels={'Amount': 'Total Sales ($)'}
)
fig1.update_layout(template="plotly_white")
plotly(fig1)

# Sales by Product
text(
    "## Sales by Product \n This bar chart displays the total sales for each chocolate product."
)
product_sales = chocolate_df.groupby('Product')['Amount'].sum().reset_index().sort_values('Amount', ascending=False)
fig2 = px.bar(
    product_sales,
    x='Product',
    y='Amount',
    title='Total Sales by Product',
    labels={'Amount': 'Total Sales ($)'}
)
fig2.update_layout(template="plotly_white", xaxis={'categoryorder': 'total descending'})
plotly(fig2)

# Sales Person Performance
text(
    "## Sales Person Performance \n This bar chart compares the total sales achieved by each sales person."
)
salesperson_sales = chocolate_df.groupby('Sales Person')['Amount'].sum().reset_index().sort_values('Amount', ascending=False)
fig3 = px.bar(
    salesperson_sales,
    x='Sales Person',
    y='Amount',
    title='Total Sales by Sales Person',
    labels={'Amount': 'Total Sales ($)'},
)
fig3.update_layout(template="plotly_white")
plotly(fig3)

# Amount vs Boxes Shipped
text(
    "## Amount vs Boxes Shipped \n This scatter plot shows the relationship between sales amount and the number of boxes shipped. This helps identify high-value vs. high-volume sales."
)
fig4 = px.scatter(
    chocolate_df,
    x='Boxes Shipped',
    y='Amount',
    color='Product',
    hover_data=['Sales Person', 'Country', 'Date'],
    title='Sales Amount vs Boxes Shipped',
)
fig4.update_layout(template="plotly_white")
plotly(fig4)

# Monthly Sales Trend
text(
    "## Monthly Sales Trend \n This line chart tracks the total sales amount over time (by month)."
)
monthly_sales = chocolate_df.groupby(chocolate_df['Date'].dt.strftime('%Y-%m'))['Amount'].sum().reset_index()
monthly_sales.columns = ['Month', 'Amount']
fig5 = px.line(
    monthly_sales,
    x='Month',
    y='Amount',
    title='Monthly Sales Trend',
    labels={'Amount': 'Total Sales ($)', 'Month': 'Month (2022)'},
    markers=True,
)
fig5.update_layout(template="plotly_white")
plotly(fig5)

# Price Per Box by Product
text(
    "## Price Per Box by Product \n This bar chart shows the average price per box for each product, indicating product value."
)
price_per_box = chocolate_df.groupby('Product')['Price Per Box'].mean().reset_index().sort_values('Price Per Box', ascending=False)
fig6 = px.bar(
    price_per_box,
    x='Product',
    y='Price Per Box',
    title='Average Price Per Box by Product',
    labels={'Price Per Box': 'Avg Price Per Box ($)'},
)
fig6.update_layout(template="plotly_white")
plotly(fig6)

# Product Distribution by Country
text(
    "## Product Distribution by Country \n This stacked bar chart shows the sales breakdown of different products within each country."
)
country_product = chocolate_df.groupby(['Country', 'Product'])['Amount'].sum().reset_index()
fig7 = px.bar(
    country_product,
    x='Country',
    y='Amount',
    color='Product',
    title='Product Sales Distribution by Country',
    labels={'Amount': 'Sales Amount ($)'},
)
fig7.update_layout(template="plotly_white")
plotly(fig7)

# Show the dataset
text(
    "## Sample of the Chocolate Sales Dataset \n Below is a preview of the sales data."
)
table(chocolate_df, limit=10)
