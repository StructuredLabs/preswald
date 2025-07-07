from preswald import text, plotly, connect, get_df, table,query
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

connect()
df = get_df('Ecommerce_Delivery_Analytics_New')
print(f"Data loaded successfully! {df}")

sql = "SELECT * FROM Ecommerce_Delivery_Analytics_New WHERE service_rating > 3"
filtered_df = query(sql, "Ecommerce_Delivery_Analytics_New")
table(filtered_df, title="Filtered Data")


fig = px.scatter(df, x='order_date', y='service_rating', text='service_rating',
                 title='order_date vs. service_rating',
                 labels={'order_date': 'service_rating', 'service_rating': 'service_rating'})
fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

fig.update_layout(template='plotly_white')

plotly(fig)

