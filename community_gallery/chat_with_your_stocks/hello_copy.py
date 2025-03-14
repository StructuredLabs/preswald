from preswald import text, plotly, connect, get_df, table , query ,button
import pandas as pd
import plotly.express as px

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')


# Create a scatter plot
fig = px.scatter(df, x='quantity', y='value', text='item',
                 title='Quantity vs. Value',
                 labels={'quantity': 'Quantity', 'value': 'Value'})

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# Style the plot
fig.update_layout(template='plotly_white')

# Show the plot
plotly(fig)


# Show the data
table(df)


sql = "SELECT * FROM sample_csv"
filtered_df = query(sql, "sample_csv")

text("# My Data Analysis App")
table(filtered_df, title="Filtered Data")

#button(label: str, size: float = 1.0)
button(label="Click Me babee!!")

def generate_simple_analysis(df):
    sql = "SELECT * FROM {df}"
    filtered_df = query(sql, "sample_csv")
    
    text("# Welcome to Preswald")
    table(filtered_df, title="Filtered Data" , limit=10)
####
from preswald import checkbox, text

# Create a checkbox for selecting 
money_shown = checkbox(label="Show me the money")
if money_shown:
    text("The money")

##########
from preswald import progress
import time

# Simple progress example
progress(label="Current Progress", value=50.3)  # will display as 50%

# Progress in a loop
for i in range(10):
    # Update progress as work is done
    progress(label="Processing Files", value=i * 10)
    time.sleep(0.5)  # Simulate work being done


from preswald import selectbox

# Create a dropdown menu to select a dataset
choice = selectbox(
    label="Choose Dataset",
    options=["Dataset A", "Dataset B", "Dataset C"]
)

# Use the selected option
print(f"User selected: {choice}")



#####
from preswald import text

# Display a Markdown header
text("# Welcome to Preswald")

# Display a paragraph
text("This is a **formatted text** example using Markdown.")

text("## Inputt Texts")
from preswald import text_input, text, alert

# Basic text input
name = text_input(label="Enter your name", placeholder="John Doe")

# Using text input in a form
email = text_input(label="Email", placeholder="user@example.com")
password = text_input(label="Password", placeholder="Enter password")

if name and email and password:
    alert(f"Welcome {name}!", level="success")