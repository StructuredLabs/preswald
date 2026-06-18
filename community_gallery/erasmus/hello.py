from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px

text("# My Data Analysis App")
# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('erasmus_csv')

from preswald import query

sql = "SELECT * FROM erasmus_csv WHERE 'EXAM SCORE' > '80'"
filtered_df = query(sql, "erasmus_csv")


# Create a scatter plot
fig = px.scatter(df, x='EXAM SCORE', y='GRANT', text='COUNTRIES',
                 title='Exam vs. Grant',
                 labels={'exam': 'Exam', 'grant': 'Grant'})

# Add labels for each point
fig.update_traces(textposition='top center', marker=dict(size=12, color='lightblue'))

# Style the plot
fig.update_layout(template='plotly_white')

from preswald import slider
threshold = slider("Threshold", min_val=60, max_val=100, default=80)
table(df[df["EXAM SCORE"] > threshold], title="Dynamic Data View")

# Show the plot
plotly(fig)

# Show the data
#table(filtered_df)
