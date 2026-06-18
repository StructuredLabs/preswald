from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

text("# Grocery Inventory Manager")
text("## Monitor grocery inventory for low stock items.")
text("The Slider displays all items with less than the threshold in stock. Duplicates may stack.")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('Grocery_Inventory')

# Add slider
threshold = slider("Threshold", min_val=0, max_val=100, default=30)

# Show the plot
fig = px.bar(df[df['Stock_Quantity'] < threshold], x='Product_Name', y='Stock_Quantity', title='Grocery Inventory')
plotly(fig)

'''
Get all items from inventory with less than 30 units in stock
and filter out any discontinued or backordered items
'''
sql = "SELECT * from Grocery_Inventory WHERE Stock_Quantity < 30 and Status NOT IN ('Discontinued', 'Backordered')"
filtered_df = query(sql, 'Grocery_Inventory')

text("## Items with < 30 units")
table(filtered_df[filtered_df['Stock_Quantity'] < threshold], title="Grocery Inventory")
