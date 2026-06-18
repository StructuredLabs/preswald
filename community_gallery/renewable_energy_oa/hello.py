from preswald import text, plotly, connect, table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Connect to preswald
connect()

# Load the CSV
df = pd.read_csv("data/renewable_energy.csv")

text("# Comprehensive Analysis of Global Renewable Energy Adoption (1965-2021)")
text("Hello there! Welcome to the Global Renewable Energy Dashboard, where we explore adoption of clean energy across the world. This analysis mainly features renewable energy adoption trends across major countries, including multiple visualizations to provide different perspectives on the data.")

text("""
## Trend Analysis
The line graph below shows the continuous progression of renewable energy adoption, which is more relevant than ever in today's world:
- The World average shows steady growth, particularly accelerating after 2000
- Germany demonstrates remarkable growth, especially post-2000
- China shows rapid adoption in recent years
- The United States shows consistent but moderate growth
- The United Kingdom shows significant acceleration in recent years
""")

# Select major countries for visualization
countries = ['United States', 'China', 'Germany', 'United Kingdom', 'World']
df_filtered = df[df['Entity'].isin(countries)]

# Calculate 5-year averages for each country
df_filtered['Period'] = (df_filtered['Year'] // 5) * 5
period_averages = df_filtered.groupby(['Entity', 'Period'])['Renewables (% equivalent primary energy)'].mean().reset_index()

# Main trend line plot
fig1 = px.line(df_filtered, 
              x='Year', 
              y='Renewables (% equivalent primary energy)',
              color='Entity',
              title='Renewable Energy Adoption Trends by Country (1965-2021)',
              labels={
                  'Year': 'Year',
                  'Renewables (% equivalent primary energy)': 'Renewable Energy Share (%)',
                  'Entity': 'Country'
              })

fig1.update_layout(
    template='plotly_white',
    hovermode='x unified',
    xaxis_title="Year (1965-2021)",
    yaxis_title="Renewable Energy Share (% of Total Energy)",
    legend_title="Country",
    plot_bgcolor='white',
    title_x=0.5, 
    font=dict(size=12)
)
# Show the first plot
plotly(fig1)

text("""
The bar graph below provides a detailed view of renewable energy adoption in 5-year intervals since 2000:
- Germany leads the pack with the highest average adoption rates, reaching over 20% in recent periods
- The United Kingdom shows the most dramatic improvement, nearly tripling its renewable share
- China demonstrates accelerating growth, particularly in the 2015-2020 period
- The United States maintains steady but modest growth across all periods
- The World average reflects the combined impact, showing consistent upward momentum
- The 2015-2020 period shows the highest adoption rates across all entities, indicating global momentum
""")

# Bar chart
recent_period = period_averages[period_averages['Period'] >= 2000]
fig2 = px.bar(recent_period,
              x='Period',
              y='Renewables (% equivalent primary energy)',
              color='Entity',
              barmode='group',
              title='Average Renewable Energy Adoption by 5-Year Periods (2000-2020)',
              labels={
                  'Period': '5-Year Period Starting',
                  'Renewables (% equivalent primary energy)': 'Average Renewable Share (%)',
                  'Entity': 'Country'
              })

fig2.update_layout(
    template='plotly_white',
    xaxis_title="5-Year Period Starting",
    yaxis_title="Average Renewable Share (%)",
    legend_title="Country"
)

plotly(fig2)


text("""
The scatter plot below reveals the distribution and magnitude of renewable energy adoption since 2000:
- Point sizes reflect the magnitude of renewable energy share, with larger points indicating higher adoption rates
- Germany's points grow notably larger over time, showing substantial progress in renewable adoption
- The United Kingdom shows an upward trajectory with increasing point sizes in recent years
- China's points remain smaller but show consistent upward movement, indicating steady progress
- The United States displays moderate-sized points with gradual upward movement
- The World average points show steady growth in size, reflecting global progress
- The clustering of larger points in recent years (2015-2021) demonstrates accelerated adoption across all entities
""")

# Scatter plot
fig3 = px.scatter(df_filtered[df_filtered['Year'] >= 2000],
                 x='Year',
                 y='Renewables (% equivalent primary energy)',
                 color='Entity',
                 size='Renewables (% equivalent primary energy)',
                 title='Renewable Energy Adoption Distribution (2000-2021)',
                 labels={
                     'Year': 'Year',
                     'Renewables (% equivalent primary energy)': 'Renewable Energy Share (%)',
                     'Entity': 'Country'
                 })

fig3.update_layout(
    template='plotly_white',
    xaxis_title="Year (2000-2021)",
    yaxis_title="Renewable Energy Share (%)",
    legend_title="Country",
    title_x=0.5,
    font=dict(size=12)
)

plotly(fig3)

# Calculate and display summary statistics
text("""
## Statistical Summary (2015-2021)
Below is a detailed analysis of recent adoption rates for each country/region:
- Average: Mean renewable energy adoption rate over the period
- Minimum: Lowest recorded rate during the period
- Maximum: Highest recorded rate during the period
""")

recent_stats = df_filtered[df_filtered['Year'] >= 2015].groupby('Entity').agg({
    'Renewables (% equivalent primary energy)': ['mean', 'min', 'max']
}).round(2)

recent_stats = recent_stats.reset_index()
recent_stats = recent_stats.rename(columns={'Entity': 'Country/Region'})

table(recent_stats)

text("""
## Key Insights from the Visualizations:

1. **Long-term Trends (Line Graph)**:
   - Shows the complete historical progression from 1965 to 2021
   - Highlights acceleration points and periods of significant change
   - Demonstrates relative positions of countries throughout the timeline

2. **5-Year Averages (Bar Chart)**:
   - Provides a clearer view of medium-term progress
   - Reduces annual fluctuations for better trend visibility
   - Enables easy comparison between countries in specific time periods

3. **Growth Trends (Scatter Plot)**:
   - Linear regression lines show the rate of adoption
   - Highlights which countries have the steepest growth rates
   - Shows the variability in annual data points

4. **Statistical Summary**:
   - Provides concrete numbers for recent performance
   - Shows the range of adoption rates in recent years
   - Helps quantify the differences between countries
""")