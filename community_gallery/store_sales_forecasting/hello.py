from preswald import connect, get_df, plotly, query, slider, table, text
import pandas as pd
import plotly.express as px


# Load the CSV
connect()  # load in all sources, which by default is the sample_csv
df = get_df("stores_sales_forecasting")

# top selling items
top_selling_query = 'SELECT "Product ID","Product Name", COUNT(Quantity) FROM stores_sales_forecasting GROUP BY "Product ID","Product Name" ORDER BY COUNT(Quantity) DESC LIMIT 5'
top_selling_df = query(top_selling_query, "stores_sales_forecasting")
text("## Top Selling Items")
table(top_selling_df, "Top Selling Items")

#Most valuable customers
valuable_customers_query = 'SELECT "Customer ID","Customer Name", SUM(Sales), Count("Order ID") FROM stores_sales_forecasting GROUP BY "Customer ID","Customer Name" ORDER BY SUM(Sales) DESC LIMIT 5'
valuable_customers_df = query(valuable_customers_query, "stores_sales_forecasting")
text("## Most Valuable Customers")
table(valuable_customers_df, "Most Valuable Customers")

#Profitable orders
threshold = slider("Profit Threshold", min_val=0, max_val=1000, default=100)
profitable_orders_query = 'SELECT * FROM stores_sales_forecasting WHERE Profit>0 ORDER BY Profit DESC'
profitable_orders_df = query(profitable_orders_query, "stores_sales_forecasting")
text("## Profitable Orders")
table(profitable_orders_df[profitable_orders_df["Profit"]>threshold], "Profitable Orders")
# Orders by State
state_query = 'SELECT "State", COUNT(Quantity) FROM stores_sales_forecasting GROUP BY "State" ORDER BY COUNT(Quantity) DESC'
state_df = query(state_query, "stores_sales_forecasting")
text("## Orders by State")
fig_order_by_state = px.bar(
    state_df,
    x="State",
    y="count(Quantity)",
    title="Orders by State",
    labels={"State": "State", "count(Quantity)": "Order count"},
)
plotly(fig_order_by_state)
#top cities by sales count
top_cities_query = 'SELECT "City", COUNT(Quantity) FROM stores_sales_forecasting GROUP BY "City" ORDER BY COUNT(Quantity) DESC LIMIT 10'
top_cities_df = query(top_cities_query, "stores_sales_forecasting")
text("## Top Cities by Sales Count")
fig_top_cities=px.pie(top_cities_df, values="count(Quantity)", names="City", title="Top Cities by Sales Count")
plotly(fig_top_cities)


#Correlation Heatmap
correlation_heatmap = df[["Profit", "Discount", "Quantity", "Sales"]].corr()
text("## Correlation Heatmap")
fig_correlation_heatmap = px.imshow(correlation_heatmap)
plotly(fig_correlation_heatmap)