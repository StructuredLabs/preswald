from preswald import text, plotly, connect, get_df, table
import pandas as pd
import plotly.express as px

act = '#1f77b4'  # Blue
rec = '#2ca02c'  # Green
dth = '#d62728'  # Red

text("# Welcome to Preswald!")
text("This is your first app. 🎉")
text("Covid-19 Analysis")

# Load the CSV
connect() 

day_wise = get_df('day_csv')
country = get_df('country_csv')
usa = get_df('usa_csv')



day_wise['Date'] = pd.to_datetime(day_wise['Date'])

temp = day_wise[['Date','Deaths', 'Recovered', 'Active']].tail(1)
temp = temp.melt(id_vars="Date", value_vars=['Active', 'Deaths', 'Recovered'])
fig = px.treemap(temp, path=["variable"], values="value", height=225, 
                 color_discrete_sequence=[act, rec, dth])
fig.data[0].textinfo = 'label+text+value'

def plot_hbar(df, col, n, hover_data=[]):
    fig = px.bar(df.sort_values(col).tail(n), 
                 x=col, y="Country/Region", color='WHO Region',  
                 text=col, orientation='h', width=700, hover_data=hover_data,
                 color_discrete_sequence = px.colors.qualitative.Dark2)
    fig.update_layout(title=col, xaxis_title="", yaxis_title="", 
                      yaxis_categoryorder = 'total ascending',
                      uniformtext_minsize=8, uniformtext_mode='hide')
    plotly(fig)

plot_hbar(country, 'Confirmed', 15)


plotly(fig)


table(day_wise)
