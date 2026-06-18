from preswald import text, plotly, connect, get_df, table, slider, selectbox
import pandas as pd
import plotly.express as px
from preswald import query

# Connect and Load Data
connect()
df = get_df('sample_csv')
my_dataset = 'sample_csv'

text("## Car Data Dashboard")
text("Explore your car dataset by selecting a car brand, color, and setting a minimum price threshold.")

car_names = ['All', 'Accord', 'Altima', 'CX-5', 'Camry', 'Civic', 'Corolla', 'Elantra',
             'Explorer', 'Impreza', 'Model 3', 'Model S', 'Mustang', 'Rav4', 'Sentra', 'Tucson']
car_colors = ['All', 'Black', 'Blue', 'Green', 'Grey', 'Maroon', 'Orange', 'Red', 'Silver', 'White', 'Yellow']

selected_car = selectbox("Select Car Model", car_names)
selected_color = selectbox("Select Car Color", car_colors)
threshold = slider("Minimum Price Threshold", min_val=0, max_val=60000, default=0)


if selected_car == 'All' and selected_color == 'All':
    sql = f"SELECT * FROM {my_dataset} WHERE value >= {threshold}"
elif selected_car == 'All':
    sql = f"SELECT * FROM {my_dataset} WHERE color = '{selected_color}' AND value >= {threshold}"
elif selected_color == 'All':
    sql = f"SELECT * FROM {my_dataset} WHERE name = '{selected_car}' AND value >= {threshold}"
else:
    sql = f"SELECT * FROM {my_dataset} WHERE name = '{selected_car}' AND color = '{selected_color}' AND value >= {threshold}"


filtered_df = query(sql, my_dataset)
table(filtered_df, title="Filtered Cars by Brand, Color & Price")

if filtered_df is not None and not filtered_df.empty:
    if selected_car != 'All':
        bar_fig = px.bar(filtered_df.groupby('color')['value'].sum().reset_index(),
                         x='color', y='value',
                         title=f'Total Price by Color for {selected_car}',
                         labels={'color': 'Color', 'value': 'Total Price'})
    else:
        bar_fig = px.bar(filtered_df.groupby('name')['value'].sum().reset_index(),
                         x='name', y='value',
                         title='Total Price by Car Brand',
                         labels={'name': 'Car Brand', 'value': 'Total Price'})
    
    plotly(bar_fig)

    pie_fig = px.pie(filtered_df, names='color', title='Color Distribution of Selected Cars')
    plotly(pie_fig)
else:
    text("No data available for the selected filters.")
