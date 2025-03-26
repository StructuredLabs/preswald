from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')

#Create a pie chart
fig_pie = px.pie(df, values="Purchase Amount (USD)", names = "Payment Method")

#Create a bar plot
fig_bar = px.bar(df, x="Item Purchased", y = "Purchase Amount (USD)", color = "Category" )

# Show the pie chart and plot
text("# My Data Analysis App")
text("Pie Chart of Payment Methods")
plotly(fig_pie)
text("Amount of Each Item Purchased")
plotly(fig_bar)


# Manipulate the data into readable format
if "Subscription Status" or "Discount Applied" or "Promo Code Used" in df.columns:
    df["Subscription Status"] = df["Subscription Status"].astype(str)
    df["Discount Applied"] = df["Discount Applied"].astype(str)
    df["Promo Code Used"] = df["Promo Code Used"].astype(str)


#Query the data and select specific comlumns
from preswald import query
sql = 'SELECT "Customer ID", Age, Gender, "Item Purchased", "Purchase Amount (USD)", "Payment Method", CASE WHEN "Subscription Status" = 1 THEN 1 ELSE 0 END "Subscription Status", CASE WHEN "Subscription Status" = 1 THEN 1 ELSE 0 END "Discount Applied", CASE WHEN "Promo Code Used" = 1 THEN 1 ELSE 0 END "Promo Code Used" FROM sample_csv'
filtered_df = query(sql, "sample_csv")

#Build UI components
text("# Filtered Data")
table(filtered_df, title="Filtered Data Based on Subscription Status, Discount Applied and Promo Code Used")

#Add user controls
from preswald import slider
text('Filtered Data based on Purchase Amount (USD)')
threshold = slider("Purchase Amount (USD)", min_val=0, max_val=100, default=50)
table(df[df["Purchase Amount (USD)"] > threshold], title="Dynamic Data View")