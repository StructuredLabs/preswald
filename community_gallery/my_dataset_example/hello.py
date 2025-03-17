from preswald import connect, get_df, table, text, slider, plotly
import plotly.express as px

# Connect to the dataset
connect()
df = get_df("best_selling_manga.csv")  # Ensure this filename matches!

# Print dataset to check
print(df.head())  # ✅ DEBUGGING STEP

# App title
text("# Best-Selling Manga Data Explorer 📚")

# Show dataset preview
table(df.head(), title="Preview of Best-Selling Manga")

# Slider for filtering by sales
threshold = slider("Minimum Copies Sold (millions)", 
                   min_val=df["Approximate sales in million(s)"].min(), 
                   max_val=df["Approximate sales in million(s)"].max(), 
                   default=50)

# Filter dataset based on user input
filtered_df = df[df["Approximate sales in million(s)"] >= threshold]

# Display filtered table
table(filtered_df, title=f"Manga with at Least {threshold} Million Copies Sold")

# Bar chart visualization
fig = px.bar(filtered_df, 
             x="Manga series", 
             y="Approximate sales in million(s)", 
             color="Author(s)", 
             title="Top-Selling Manga of All Time",
             labels={"Manga series": "Manga", "Approximate sales in million(s)": "Sales (Millions)"})

# Show the chart
plotly(fig)
