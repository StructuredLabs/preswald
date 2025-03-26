from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

# Initialize connection to preswald.toml data sources
connect()

text("## Data")

# Retrieve data from the CSV file
show_df = pd.read_csv('./data/chocolate.csv')

# Scatter Plot
text("### Boxes Shipped vs. Amount")
text("This plot visualizes the relationship between the number of boxes shipped and the total sales amount. Each point represents a product, and the color indicates the product category. Hover over the points to see additional details such as the sales person and country.")
fig = px.scatter(show_df, x='Boxes Shipped', y='Amount', color='Product', 
                 title='Boxes Shipped vs. Amount', 
                 hover_data=['Sales Person', 'Country'],
                 color_continuous_scale=px.colors.sequential.Viridis)
plotly(fig)

# Bar Chart
text("### Bar Chart: Total Amount by Product")
text("This plot displays the total sales amount for each product. The bars are colored by country, providing a visual comparison of sales across different regions. Hover over the bars to see additional information about the sales person and the number of boxes shipped.")
fig = px.bar(show_df, x='Product', y='Amount', title='Total Amount by Product', 
             color='Country', 
             hover_data=['Sales Person', 'Boxes Shipped'],
             color_continuous_scale=px.colors.sequential.Plasma)
plotly(fig)

# Line Chart
text("### Line Chart: Amount Over Time")
text("This plot shows the trend of sales amounts over time. Each line represents a product, allowing you to see how sales for different products have changed over the specified period. Hover over the lines to see additional details such as the sales person and country.")
fig = px.line(show_df, x='Date', y='Amount', title='Amount Over Time', 
              color='Product', 
              hover_data=['Sales Person', 'Country'],
              color_discrete_sequence=px.colors.qualitative.Bold)
plotly(fig)

# Histogram
text("### Distribution of Amounts")
text("This plot shows the distribution of sales amounts. The bars are colored by product category, providing a visual representation of how sales amounts are distributed across different products.")
fig = px.histogram(show_df, x='Amount', title='Distribution of Amounts', 
                   color='Product', 
                   color_discrete_sequence=px.colors.qualitative.Pastel)
plotly(fig)