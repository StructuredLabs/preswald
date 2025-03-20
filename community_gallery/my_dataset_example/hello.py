from preswald import connect, get_df, table, text, slider, plotly
import plotly.express as px

# Connect to the dataset
connect()

# Load the dataset
df = get_df("manga_csv")

# Debug: Print dataset structure
print("Dataset loaded successfully!")
print(df.head())

# Rename columns to remove special characters (avoiding potential issues)
df = df.rename(columns={"Approximate sales in million(s)": "SalesMillions"})

# App title
text("# Best-Selling Manga Data Explorer 📚")

# Show dataset preview
table(df.head(), title="Preview of Best-Selling Manga")

# Debug: Print min/max sales values
print(f"Sales Range: Min={df['SalesMillions'].min()}, Max={df['SalesMillions'].max()}")

# Slider for filtering by sales
threshold = slider(
    "Minimum Copies Sold (millions)", 
    min_val=df["SalesMillions"].min(), 
    max_val=df["SalesMillions"].max(), 
    default=50
)

# Filter dataset based on user input
filtered_df = df[df["SalesMillions"] >= threshold]

# Debug: Ensure filtered data is not empty
print(f"Filtered rows: {len(filtered_df)}")
if filtered_df.empty:
    text("⚠️ No manga found with the selected sales threshold.")

# Display filtered table
table(filtered_df, title=f"Manga with at Least {threshold} Million Copies Sold")

# Bar chart visualization (Only if data is available)
if not filtered_df.empty:
    fig = px.bar(
        filtered_df, 
        x="Manga series", 
        y="SalesMillions", 
        color="Author(s)", 
        title="Top-Selling Manga of All Time",
        labels={"Manga series": "Manga", "SalesMillions": "Sales (Millions)"}
    )

    # Show the chart
    plotly(fig)
else:
    text("📊 No data available for plotting. Adjust the slider to see results.")
