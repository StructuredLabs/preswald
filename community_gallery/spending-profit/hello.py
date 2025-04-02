from preswald import text, plotly, connect, get_df, table, query, slider
import plotly.express as px

text("Nageswari's Assessment")

connect()

df = get_df('sample_csv')
df.drop(labels=['State'], axis=1, inplace=True)

# Plot a bar chart to show the average amount for each type of spending
column_header = list(df.columns)
spending_dict = {}

for col in df:
    if col != "Profit":
        spending_dict[col] = int(df[col].mean())

fig_bar = px.bar(
    x=list(spending_dict.keys()),
    y=list(spending_dict.values()),
    text=['R&D Spend', 'Administration', 'Marketing Spend'],
    title='Average amount for each type of spending',
    labels={'x': 'Spending', 'y': 'Amount'},
    color_discrete_sequence=['#800080']
)

fig_bar.update_layout(template='plotly_white', yaxis=dict(showgrid=False))
plotly(fig_bar)

# Filter the data to show only rows where Profit is greater than 120000
sql = "SELECT * FROM sample_csv WHERE Profit > 120000"
filtered_df = query(sql, "sample_csv")
table(filtered_df, title="Filtered Data where Profit is greater than 120000")

# Filter the data to show only rows where Profit is greater than threshold
threshold = slider("Threshold", min_val=40000, max_val=170000, default=100)
table(df[df["Profit"] > threshold], title="Dynamic Data View")