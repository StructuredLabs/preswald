from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import plotly.express as px

text("# IPL 2024 Auction Data")

# Load the CSV
connect() # load in all sources, which by default is the sample_csv
df = get_df('auction_csv')
df['PRICE PAID'] = pd.to_numeric(df['PRICE PAID'])

text("Use the slider below to findout the Indian/Overseas play analysis")
threshold = slider("price threshold", min_val=2000000, max_val=247500000, default=53322513)
filtered_df = df[df['PRICE PAID'] >= threshold]

# Creating a pie plot
fig = px.pie(filtered_df, 
             names='NATIONALITY', 
             title=f'Overseas vs Indian Players (Price >= {threshold: ,})')


plotly(fig)
# creating a histogram
fig2 = px.histogram(df, 
                   x='PRICE PAID', 
                   nbins=30,
                   title='Price Distribution Histogram')

plotly(fig2)
# creating a strip plot
fig = px.strip(df, 
              x='TYPE', 
              y='PRICE PAID', 
              title='Price Distribution Across Roles')
fig.update_layout(xaxis={'categoryorder':'total descending'})
plotly(fig)

