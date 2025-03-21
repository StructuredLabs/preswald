from preswald import connect, get_df, table, text, plotly, slider
import plotly.express as px

# Initialize connection and load dataset
connect()
df = get_df("superstore_sales")

# Validate if dataset is loaded correctly
if df is None:
    text("Error: Dataset not found. Check `preswald.toml` and ensure `train.csv` is correctly registered.")
else:
    # Dashboard Title
    text("## Sales Performance Dashboard")

    # User-Controlled Sales Threshold
    min_sales, max_sales = df["Sales"].min(), df["Sales"].max()
    threshold = slider("Set Sales Threshold ($)", min_val=min_sales, max_val=max_sales, default=500)

    # Apply the selected threshold to filter sales records
    filtered_df = df[df["Sales"] > threshold].copy()

    # Handle case when no data matches the selected threshold
    if filtered_df.empty:
        text("No sales records meet the selected threshold. Try adjusting the slider.")
    else:
        # Display Top 5 Highest Sales Transactions
        top_sales_df = df.nlargest(5, "Sales")
        text("### Top 5 Sales Records")
        table(top_sales_df)

        # Sales Breakdown by Sub-Category
        category_sales = filtered_df.groupby("Sub-Category")["Sales"].sum().reset_index()
        if not category_sales.empty:
            fig = px.bar(
                category_sales,
                x="Sub-Category",
                y="Sales",
                color="Sub-Category",
                title="Sales Breakdown by Sub-Category",
            )
            fig.update_layout(xaxis={"categoryorder": "total descending"})
            plotly(fig)
        else:
            text("No sales breakdown available for the selected threshold.")

        # Filtered Sales Records Table
        text("### Filtered Sales Records")
        sorted_df = filtered_df.sort_values(by="Sales", ascending=False)
        table(sorted_df)
