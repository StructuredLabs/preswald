import pandas as pd
import plotly.express as px
from preswald import text, plotly, connect, get_df, table
from preswald import query
from preswald import slider


text("# Walmart Customer Purchases Behaviour Analysis")
text("## This app analyzes customer purchase behavior at Walmart. 🎉")

# Load the CSV
connect()  
df = get_df('walmart')

sql = "SELECT Customer_ID, Age, Category, Product_Name, Purchase_Amount, Rating FROM walmart where Age > 35 ORDER BY Purchase_Amount DESC LIMIT 100" 

filtered_df = query(sql, "walmart")
# Show the data

text("## Below is the filtered data of customers older than 35, sorted by Purchase Amount:")
table(filtered_df, title="Filtered Data")


threshold = slider("Threshold", min_val=0, max_val=100, default=50)
table(df[df["Age"] > threshold], title="Dynamic Data View")

# Restrict the data to show only the top 100 rows based on Purchase_Amount
top_df = df.nlargest(50, 'Purchase_Amount')

# Create a scatter plot with enhanced appearance
fig = px.scatter(top_df, x='Age', y='Purchase_Amount', text='Product_Name',
                 title='Age vs. Purchase Amount (Top 50)',
                 labels={'Age': 'Age', 'Purchase_Amount': 'Purchase Amount'},
                 color='Category', 
                 template='plotly_white')  

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=10, opacity=0.8), textfont=dict(color='black'))

# Style the plot
fig.update_layout(
    title_font=dict(size=24, family='Arial, sans-serif', color='black'),
    xaxis=dict(title_font=dict(size=18, family='Arial, sans-serif', color='black'), tickfont=dict(color='black'), showline=True, linecolor='black'),
    yaxis=dict(title_font=dict(size=18, family='Arial, sans-serif', color='black'), tickfont=dict(color='black'), showline=True, linecolor='black'),
    plot_bgcolor='rgba(255,255,255,1)',  # White background
    paper_bgcolor='rgba(255,255,255,1)',  # White background
)

# Show the plot
plotly(fig)

text("### Thank you for using the Walmart Customer Purchases Behaviour Analysis app!")
