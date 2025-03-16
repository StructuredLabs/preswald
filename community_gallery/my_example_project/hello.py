from preswald import text, plotly, connect, get_df, table, slider
import pandas as pd
import plotly.express as px

# Initialize connection and load data
connect()
df = get_df('unicorns')

# Cleaning valuation data
df['Valuation'] = df['Valuation ($B)'].str.replace('$', '').str.replace('B', '').astype(float)

text("# 🦄 Companies Analysis")
text("Explore data about companies valued at $1 billion or more.")

# Add valuation filter
min_valuation = slider("Minimum Valuation ($B)", min_val=1, max_val=150, default=10)

# Allows user to filter data based on valuation
filtered_df = df[df['Valuation'] >= min_valuation]

# Create visualizations :)
text("## Top Companies by Valuation")
fig1 = px.bar(filtered_df.nlargest(10, 'Valuation'), 
              x='Company', y='Valuation',
              title='Top 10 Companies by Valuation',
              labels={'Valuation': 'Valuation ($B)'})
plotly(fig1)

text("## Industry Distribution")
fig2 = px.pie(filtered_df, names='Industry', 
              title='Distribution of Companies by Industry',
              hole=0.3)
plotly(fig2)

text("## Geographic Distribution")
country_data = filtered_df.groupby('Country').agg({
    'Company': 'count',
    'Valuation': 'sum'
}).reset_index()
country_data.columns = ['Country', 'Number of Companies', 'Total Valuation']

fig3 = px.scatter_geo(country_data,
                     locations='Country',
                     locationmode='country names',
                     size='Total Valuation',
                     color='Number of Companies',
                     hover_name='Country',
                     hover_data={
                         'Number of Companies': True,
                         'Total Valuation': ':.1f',
                         'Country': False
                     },
                     title='Global Distribution of 🦄 Companies',
                     size_max=50,
                     projection='orthographic',
                     color_continuous_scale='Viridis',
                     template='none')

plotly(fig3)

#Analyze industry data
text("## Industry Analysis")
industry_stats = filtered_df.groupby('Industry').agg({
    'Valuation': ['count', 'mean', 'sum']
}).round(2)
industry_stats.columns = ['Number of Companies', 'Average Valuation ($B)', 'Total Valuation ($B)']
industry_stats = industry_stats.sort_values('Total Valuation ($B)', ascending=False)
num_industries = slider("Number of industries to display", min_val=5, max_val=len(industry_stats), default=5)
table(industry_stats.head(num_industries), title=f"Top {num_industries} Industries by Total Valuation")

text("## Detailed Data")
num_companies = slider("Number of companies to display", min_val=10, max_val=len(filtered_df), default=10)
sorted_df = filtered_df.sort_values('Valuation', ascending=False)
table(sorted_df.head(num_companies), title=f"Top {num_companies} 🦄 Companies")
