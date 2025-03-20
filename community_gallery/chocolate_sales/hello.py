import pandas as pd
import plotly.express as px

from preswald import connect, get_df, plotly, selectbox, slider, table, text


# title and description
text("# Chocolate Sales Viz")
text("Visual analysis of chocolate sales for forecasting, trends, and optimization.")

# load and preprocess data
connect()
sdf = get_df("sample_csv")
df = sdf.copy()
df["Amount"] = (
    df["Amount"].replace(r"[\$,]", "", regex=True).astype(float)
)  # remove $ sign
df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%y")
df["Month"] = df["Date"].dt.strftime("%b")
df["Day"] = df["Date"].dt.day
month_order = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

# plot 1: total boxes shipped per salesperson by country
text("## Total Boxes Shipped per Salesperson")
country = selectbox(label="Country", options=df["Country"].unique().tolist(), size=1)
boxes = slider(label="Boxes Shipped", min_val=0, max_val=2500, default=0, step=100)
boxes_df = (
    df[df["Country"] == country]
    .groupby("Sales Person")["Boxes Shipped"]
    .sum()
    .reset_index()
)
boxes_df = boxes_df[boxes_df["Boxes Shipped"] > boxes]
fig = px.histogram(
    boxes_df, x="Sales Person", y="Boxes Shipped", color="Sales Person", text_auto=".2s"
)
fig.update_layout(xaxis={"type": "category", "categoryorder": "category ascending"})
plotly(fig)

# plot 2: total transactions per product
text("## Transactions per Product")
fig = px.histogram(df, x="Product", color="Product", text_auto=".2s")
plotly(fig)

# plot 3: amount distribution by sales person
text("## Amount by Sales Person")
fig = px.box(df, x="Sales Person", y="Amount", color="Sales Person")
plotly(fig)

# plot 4: amount distribution by product
text("## Amount by Product")
fig = px.box(df, x="Product", y="Amount", color="Product")
plotly(fig)

# plot 5: monthly/daily sales amount trend
text("## Monthly/Daily Sales Trend")
monthly_sales = df.groupby("Month")["Amount"].sum().reindex(month_order).reset_index()
month = selectbox(
    label="Month",
    options=["All", *monthly_sales["Month"].dropna().unique().tolist()],
    default="All",
)
if month == "All":
    monthly_sales = monthly_sales[monthly_sales["Amount"] > 0]
    fig = px.line(monthly_sales, x="Month", y="Amount", title="Total Sales by Month")
else:
    daily_sales = (
        df[df["Month"] == month]
        .groupby("Day")["Amount"]
        .sum()
        .reindex(range(1, 32), fill_value=0)
        .reset_index()
    )
    fig = px.line(daily_sales, x="Day", y="Amount", title=f"Daily Sales for {month}")
plotly(fig)

# plot 6: sales amount heatmap
text("## Sales Heatmap: Product vs Country")
fig = px.imshow(
    df.pivot_table(values="Amount", index="Product", columns="Country", aggfunc="mean"),
    text_auto=".0f",
    labels={"x": "Country", "y": "Product"},
)
plotly(fig)

# plot 7: monthly sales amount by product
text("## Monthly Sales by Product")
monthly_product_sales = df.groupby(["Month", "Product"])["Amount"].sum().reset_index()
monthly_product_sales = monthly_product_sales[monthly_product_sales["Amount"] > 0]
product = selectbox(
    label="Product",
    options=["All", *monthly_product_sales["Product"].unique().tolist()],
    default="All",
)
if product == "All":
    fig = px.area(
        monthly_product_sales,
        x="Month",
        y="Amount",
        color="Product",
        title="Monthly Sales Trends by Product",
    )
else:
    sales_data = monthly_product_sales[monthly_product_sales["Product"] == product]
    sales_data = (
        sales_data.groupby("Month")["Amount"].sum().reindex(month_order).reset_index()
    )
    fig = px.area(
        sales_data, x="Month", y="Amount", title=f"Monthly Sales Trend for {product}"
    )
plotly(fig)

# data preview
text("## Data Preview")
table(sdf, title="First 20 Rows", limit=20)
