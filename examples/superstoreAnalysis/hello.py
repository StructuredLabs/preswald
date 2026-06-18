from preswald import text, plotly, connect, get_df, table,query,slider
import plotly.express as px

text("# Welcome to Preswald!")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')

sql = "SELECT * FROM sample_csv WHERE State='California' LIMIT 100;"
filtered_df = query(sql, "sample_csv")

# Title 
text("# Superstore Analytics")
# Display Table
table(filtered_df, title="Filtered Data")


text("# Superstore Sales and Profit Analysis")
# Sales vs. Profit Plot
text("# Sales vs. Profit")
# Create a scatter plot comparing Sales to Profit
fig = px.scatter(filtered_df, x='Sales', y='Profit', color='Category',
                 title='Sales vs. Profit by Category',
                 labels={'Sales': 'Sales', 'Profit': 'Profit'})
# Style the plot
fig.update_traces(marker=dict(size=12, opacity=0.6, line=dict(width=2, color='DarkSlateGrey')))
fig.update_layout(template='plotly_white')
# Display the plot
plotly(fig)

#slider view
shipping_slider = slider("Shiping Costs",min_val=df['Shipping Cost'].min(), max_val=df['Shipping Cost'].max(), default=df['Shipping Cost'].mean())
table(filtered_df[filtered_df["Shipping Cost"] > shipping_slider], title="Dynamic Data View")

# Quantity vs. Discount Plot
text("# Quantity vs. Discount")
# Create a scatter plot comparing Quantity to Discount
fig = px.scatter(filtered_df, x='Quantity', y='Discount', color='Segment',
                 title='Quantity vs. Discount by Customer Segment',
                 labels={'Quantity': 'Quantity', 'Discount': 'Discount'})
# Style the plot
fig.update_traces(marker=dict(size=12, opacity=0.6, line=dict(width=2, color='DarkSlateGrey')))
fig.update_layout(template='plotly_white')
# Display the plot
plotly(fig)


