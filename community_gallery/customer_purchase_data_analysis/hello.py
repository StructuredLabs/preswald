from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px

# Title
text("# 📊 Ecommerce Data Analysis")
text("Analyzing customer purchases 🛍️")

# Load the dataset
connect()
df = get_df("ecommerce_data")

# Display Average Purchase Amount
sql_query = "SELECT AVG(Purchase_Amount) as AVG FROM ecommerce_data"
result = query(sql_query, "ecommerce_data")
table(result, title="📊 Average Purchase Amount")

# SQL Query: Get all purchases above $450
sql_query = "SELECT * FROM ecommerce_data WHERE Purchase_Amount > 450"
high_value_purchases = query(sql_query, "ecommerce_data")
text("### 💵 High-Value Purchases (Above $450)")
table(high_value_purchases)

# Add a Slider for Dynamic Filtering
threshold = slider("Filter by Purchase Amount", min_val=0, max_val=500, default=100)
filtered_df = df[df["Purchase_Amount"] > threshold]
table(filtered_df, title=f"Purchases Above ${threshold}")

# Create a Scatter Plot (Customer Age vs Purchase Amount)
fig = px.scatter(filtered_df, x="Age", y="Purchase_Amount", color="Purchase_Category",
                 title="Customer Spending by Age",
                 labels={"Age": "Customer Age", "Purchase_Amount": "Purchase Amount ($)"},
                 template="plotly_white")

# Improve visualization with adjusted marker size and opacity
fig.update_traces(marker=dict(size=8, opacity=0.6))

# Show the plot
plotly(fig)

# Show full dataset (optional)
table(df, title="Ecommerce Dataset")
