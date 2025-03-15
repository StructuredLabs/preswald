from preswald import text, plotly, connect, get_df, table, query, slider
import plotly.express as px

text("# Welcome to Josh McCormack's Code Assessment for Structured Labs!")
text("Enjoy perusing my application, a simple demo of Preswald and an even simpler representation of Child BMI Data!")

# Load the CSV
connect()  # Connect to the database
df = get_df('bmidata') # Get the DataFrame

# Filter the data
sql = "SELECT SchoolYear,NameHospital,Sex,EpiUnderweight,EpiHealthyWeight,EpiOverweight,EpiObese FROM bmidata" # SQL query to retrieve all data
filtered_df = query(sql, "bmidata") # Execute the query

# Show the filtered data
text("# BMI Data in Children from 2001 to 2023") # Add a title
table(filtered_df, title="Filtered Data") # Show the filtered data

threshold = slider("School Year Selector", min_val=2015, max_val=2023, default=2015) # Add a slider
table(filtered_df[filtered_df["SchoolYear"] == threshold], title="Child BMI Data by School Year") # Show the slider filtered data

# Create a scatter plot
fig = px.scatter(df, x='SchoolYear', y='EpiHealthyWeight', text='SchoolYear',
                 title='Epi Healthy Weight by School Year',
                 labels={'SchoolYear': 'School Year', 'EpiHealthyWeight': 'Value'})

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='red'))

# Style the plot
fig.update_layout(template='seaborn')

# Show the plot
plotly(fig)

# Show the data
table(df, title="Unfiltered Data")
