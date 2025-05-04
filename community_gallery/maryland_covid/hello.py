from preswald import text, plotly, connect, get_df, table, slider, selectbox
import pandas as pd
import plotly.express as px

text("# Maryland Total Covid Cases by County")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('sample_csv')

# Convert the DATE column to datetime
df['DATE'] = pd.to_datetime(df['DATE'])
df['DATE'] = df['DATE'].dt.strftime('%Y-%m-%d') 

choice = selectbox(
    label = 'County',
    default = 'Allegany',
    options = ['Allegany', 'Anne_Arundel', 'Baltimore', 'Baltimore_City', 'Calvert', 'Caroline',
                'Carroll', 'Cecil', 'Charles', 'Dorchester', 'Frederick', 'Garrett', 'Harford',
                'Howard', 'Kent', 'Montgomery', 'Prince_Georges', 'Queen_Annes', 'Somerset', 
                'St_Marys', 'Talbot', 'Washington', 'Wicomico', 'Worcester', 'Unknown'],
    size = 1
) 


fig = px.bar(df , x = 'DATE', y = choice, labels={'DATE' : 'Date', choice: 'Cases'})
plotly(fig)


