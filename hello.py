from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px

# Connect and Load the Dataset
connect()
df = get_df("sample_csv")

# Title
text("# Advanced Data Analysis App")

# Query-Based Filtering
sql = "SELECT * FROM sample_csv WHERE Price > 1.0"
filtered_df = query(sql, "sample_csv")
table(filtered_df, title="Filtered Data: Price > 1.0")

# Slider for Dynamic Price Filtering
# Slider for Minimum Rating Filter
# Sort the DataFrame by Rating in Ascending Order
# Sort the DataFrame by Rating in Ascending Order
# Slider for Rating Filtering
rating_cursor = slider("Select Minimum Rating", min_val=df["Rating"].min(), max_val=df["Rating"].max(), default=4.0)

# Filter data dynamically based on the cursor position
filtered_df = df[df["Rating"] >= rating_cursor]

# Display the dynamically filtered data
table(filtered_df, title="Products Filtered by Rating")

# Scatter Plot: Price vs. Rating
fig1 = px.scatter(df, x="Price", y="Rating", color="Category", title="Price vs. Rating")
plotly(fig1)

# Bar Chart: Category Distribution
category_counts = df["Category"].value_counts().reset_index()
category_counts.columns = ["Category", "Count"]
fig2 = px.bar(category_counts, x="Category", y="Count", title="Category Distribution")
plotly(fig2)

# Box Plot: Price Distribution per Category
fig3 = px.box(df, x="Category", y="Price", color="Category", title="Price Distribution by Category")
plotly(fig3)

# Histogram: Rating Distribution
fig4 = px.histogram(df, x="Rating", nbins=20, title="Rating Distribution", color="Category")
plotly(fig4)



