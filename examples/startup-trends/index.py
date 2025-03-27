from preswald import connect, get_df
from preswald import query
from preswald import table, text
from preswald import slider
from preswald import plotly
import plotly.express as px



connect()  # Initialize connection to preswald.toml data sources
df = get_df("startup_data_csv")  # Load data using the correct data source name

# Use proper column names from the CSV file
sql = "SELECT * FROM startup_data_csv WHERE \"Funding Amount (M USD)\" > 50"
filtered_df = query(sql, "startup_data_csv")

text("# My Startup Data Analysis App")

# Section 1: Overview
text("## Overview of Startup Data")
text(f"### Summary Statistics")
text(f"* **Total Startups**: {len(df)}")
text(f"* **Total Funding**: ${df['Funding Amount (M USD)'].sum():.2f}M USD")
text(f"* **Average Valuation**: ${df['Valuation (M USD)'].mean():.2f}M USD")
text(f"* **Profitable Startups**: {df[df['Profitable'] == 1].shape[0]} ({df[df['Profitable'] == 1].shape[0]/len(df)*100:.1f}%)")
text(f"* **Most Common Region**: {df['Region'].value_counts().index[0]}")
text(f"* **Most Common Industry**: {df['Industry'].value_counts().index[0]}")

industry_counts = df['Industry'].value_counts()
industry_fig = px.bar(
    x=industry_counts.index, 
    y=industry_counts.values,
    labels={'x': 'Industry', 'y': 'Count'},
    title="Industry Distribution"
)
plotly(industry_fig)

text("### Filtered Startup Data (Funding > $50M)")
table(filtered_df, title="Filtered Data (Funding > $50M)")

# Section 2: Interactive Analysis
text("## Interactive Data Analysis")

# Use sliders for filtering as they are available
funding_threshold = slider("Funding Threshold (M USD)", min_val=0, max_val=300, default=50)
valuation_threshold = slider("Min Valuation (M USD)", min_val=0, max_val=3500, default=0)
market_share_threshold = slider("Min Market Share (%)", min_val=0, max_val=10, default=0)

# Apply filters based on slider values
filtered_data = df[
    (df["Funding Amount (M USD)"] > funding_threshold) & 
    (df["Valuation (M USD)"] > valuation_threshold) &
    (df["Market Share (%)"] > market_share_threshold)
]

text("### Filtered Results")
table(filtered_data, title="Dynamic Data View")

# Section 3: Profitable vs Non-Profitable Analysis
text("## Profitability Analysis")
profitable_df = df[df["Profitable"] == 1]
non_profitable_df = df[df["Profitable"] == 0]

text("### Profitable Startups")
table(profitable_df.head(10), title="Top 10 Profitable Startups")

text("### Non-Profitable Startups")
table(non_profitable_df.head(10), title="Top 10 Non-Profitable Startups")

# Section 4: Visualizations
text("## Data Visualizations")

# Enhanced scatter plot
fig1 = px.scatter(df, 
                x="Funding Amount (M USD)", 
                y="Valuation (M USD)", 
                color="Industry", 
                size="Employees", 
                hover_data=["Startup Name", "Revenue (M USD)", "Market Share (%)"],
                title="Funding vs Valuation by Industry")
plotly(fig1)

# Exit status visualization
fig2 = px.pie(df, names="Exit Status", title="Distribution of Exit Status")
plotly(fig2)

# Industry distribution
fig3 = px.bar(df.groupby("Industry").size().reset_index(name="Count"), 
             x="Industry", y="Count", 
             title="Number of Startups by Industry")
plotly(fig3)

# Year founded trend
yearly_counts = df.groupby("Year Founded").size().reset_index(name="Count")
fig4 = px.line(yearly_counts, x="Year Founded", y="Count", 
              title="Startup Formation Trend by Year")
plotly(fig4)

# Region comparison
fig5 = px.box(df, x="Region", y="Funding Amount (M USD)", 
             title="Funding Distribution by Region")
plotly(fig5)