from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px

# STEP 1: Load the dataset
text("# Welcome to the Finance Data App!")
connect()  # Initialize connection (must match 'my_finance_data' in preswald.toml)
df = get_df("my_finance_data")  # Use the exact name from preswald.toml

if df is None:
    text("Dataset 'my_finance_data' could not be loaded. Check preswald.toml.")
else:
    text("Finance dataset loaded successfully!")

# STEP 2: Query or manipulate the data (SQL example)
sql = "SELECT * FROM my_finance_data WHERE Close > 200"
filtered_df = query(sql, "my_finance_data")

text("## Filtered Finance Data (Close > 200)")
table(filtered_df, title="Filtered Finance Data")

# STEP 3: Add user controls
text("### Adjust the 'Close' threshold dynamically:")
threshold = slider("Close Threshold", min_val=0, max_val=2000, default=200)

# Dynamic filter
dynamic_filtered_df = df[df["Close"] > threshold]
table(dynamic_filtered_df, title=f"Finance Data (Close > {threshold})")

# STEP 4: Create visualizations

# Minimal Volume vs Close scatter
text("## Volume vs. Close Scatter Plot")

fig_vol_close = px.scatter(
    df,
    x="Volume",
    y="Close",
    title=""
)
plotly(fig_vol_close)


# 4b) Close Price Distribution
text("## Close Price Distribution")
fig_hist = px.histogram(
    df, 
    x="Close", 
    nbins=30, 
    title="",
    color_discrete_sequence=["teal"]
)
plotly(fig_hist)
