import plotly.express as px

from preswald import connect, get_df, plotly, query, slider, table, text


text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Initialize Preswald connection
connect()

# Load dataset using Preswald
data = get_df("sample_csv")

if "Date" in data.columns:
    data["Date"] = data["Date"].astype(str)

# Query dataset for initial filtering (stocks with Close price > 100)
sql = "SELECT * FROM sample_csv WHERE Close > 5000"
filtered_df = query(sql, "sample_csv")

# Build UI components
text("# S&P 500 Stock Prices Analysis")
table(filtered_df, title="Filtered Stock Prices")

# Add interactive controls
threshold = slider("Stock Price Threshold", min_val=0, max_val=5000, default=2000)
table(data[data["Close"] > threshold], title="Dynamic Stock View")

# Create visualization: Stock price trends
fig = px.line(data, x="Date", y="Close", title="S&P 500 Stock Price Trends")
plotly(fig)
