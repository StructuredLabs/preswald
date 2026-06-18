from preswald import text, plotly, connect, table, slider
import pandas as pd
import plotly.express as px

text("# Welcome! 🚀 Chocolate Sales analysis")
text("This web app helps you manipulate and visualize the Dataset. 🎉")

connect() 

# Load the dataset manually
df = pd.read_csv('data/ChocolateSales.csv')  

# Clean the "Amount" column: Remove $, spaces, and commas
df['Amount'] = df['Amount'].replace({'\$': '', ',': '', ' ': ''}, regex=True)  
# Convert to float
df['Amount'] = pd.to_numeric(df['Amount'])  

# Drop the "Date" column
df = df.drop(columns=['Date'])

# Remove duplicates and reset index
df = df.drop_duplicates()
df.reset_index(drop=True, inplace=True)

# Display first 15 records of the original dataframe
text("### Displaying the first 15 records of the dataset:")
table(df.head(15))

# title for Dynamic vizualization. 
text("### Filtered Dataset: Amount given by user")
text("This dataset shows records where the sales amount is greater than amount selected.")

# Add a slider for dynamic threshold
threshold = slider("Threshold (Amount)", min_val=0, max_val=20000, default=5000)

# Dynamic table filtering based on slider input
filtered_df = df[df['Amount'] > threshold]
text(f"### Displaying records where 'Amount' is greater than {threshold}:")

# Display the filtered data
table(filtered_df.head(15))

# Visualization for filtered data
fig = px.bar(filtered_df, x='Product', y='Amount', title=f"Sales for Amount > {threshold}")
fig.update_layout(template='plotly_white')
plotly(fig)

# SQL filtering 

# 1. Filter for 'Amount' > 10000
df1 = df[df['Amount'] > 10000]
text("### Filtered Dataset: Amount > 10000")
text("This dataset shows records where the sales amount is greater than 10,000.")
table(df1.head(15))

# Visualization for df1
fig1 = px.scatter(df1, x='Product', y='Amount', size='Boxes Shipped', title="Amount > 10000")
fig1.update_layout(template='plotly_white')
plotly(fig1)


# 2. Filter for 'Product' = 'Smooth Sliky Salty' or '99% Dark & Pure'
df2 = df[df['Product'].isin(['Smooth Sliky Salty', '99% Dark & Pure'])]
text("### Filtered dataset for Product in ['Smooth Sliky Salty', '99% Dark & Pure']:")
table(df2.head(15))

# Visualization for df2
fig2 = px.bar(df2, x='Product', y='Amount', title="Sales for Smooth Sliky Salty & 99% Dark & Pure")
text("### Filtered Dataset: Product in ['Smooth Sliky Salty', '99% Dark & Pure']")
text("This dataset shows records for the products 'Smooth Sliky Salty' and '99% Dark & Pure'.")
fig2.update_layout(template='plotly_white')
plotly(fig2)

# 3. Filter for 'Amount' between 3000 and 5000
df3 = df[(df['Amount'] >= 3000) & (df['Amount'] <= 5000)]
text("### Filtered dataset for Amount between 3000 and 5000:")
table(df3.head(15))

# Visualization for df3
fig3 = px.box(df3, x='Product', y='Amount', title="Amount between 3000 and 5000")
text("### Filtered Dataset: Amount between 3000 and 5000")
text("This dataset shows records where the sales amount is between 3,000 and 5,000.")
fig3.update_layout(template='plotly_white')
plotly(fig3)