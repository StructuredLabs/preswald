from preswald import text, plotly, connect, get_df, table, query, slider
import pandas as pd
import plotly.express as px

# df = pd.read_csv("/Users/akhilenderk/Desktop/Assessment_preswald/Metro_Interstate_Traffic_Volume.csv") #Reading CSV
# df.drop(columns='holiday',inplace=True) #Dropping null column
# df.to_csv("data/cleaned_traffic_volume.csv") #Saving the dataset


text("# Welcome to Real Time Traffic Volume Analysis!")
text('''Steps to use the App:
- Use the slider to set the desired threshold for traffic volume.
- The App then queries your value and visualizes the results as a Scatterplot.''')


# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')

sql = "SELECT * FROM sample_csv WHERE traffic_volume > 3000 LIMIT 10"
query_df = query(sql, "sample_csv")

threshold = slider("Threshold", min_val=100, max_val=9000, default= 3000)
filtered_df = query_df[query_df['traffic_volume'] > threshold]


# Create a scatter plot
fig = px.scatter(filtered_df, x='temp', y='traffic_volume', 
                 hover_name='weather_description',
                 title='Traffic Volume vs. Weather Temperature',
                 labels={'quantity': 'Traffic Volume', 'price': 'Weather Temperature'})

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='darkgray'))

# Style the plot
fig.update_layout(template='plotly_white',
                  xaxis_title='Weather Temperature',
                  yaxis_title='Traffic Volume')

# Show the plot
plotly(fig)

# Show the data
table(filtered_df,title="User Filtered Data")
