import pandas as pd
from preswald import connect, get_df, table, text, slider, selectbox, checkbox, plotly
import plotly.express as px

# ✅ Connect to dataset
connect()
df = get_df("chocolate_sales")

if df is None:
    text("⚠️ **Error: Dataset not found. Check file path!**")
    exit()

df.columns = df.columns.str.strip()

# ✅ Ensure required columns
required_columns = {"Sales Person", "Country", "Product", "Date", "Amount", "Boxes Shipped"}
missing_columns = required_columns - set(df.columns)
if missing_columns:
    text(f"⚠️ **Error: Missing columns in dataset: {', '.join(missing_columns)}**")
    exit()

# ✅ Fix data types
df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%y", errors="coerce")
df["Amount"] = df["Amount"].astype(str).str.replace(r"[$,\s]", "", regex=True).astype(float)
df["Date_str"] = df["Date"].dt.strftime("%Y-%m-%d")

# 🎨 **Dashboard Header**
text("# 🏆🍫 Chocolate Sales Dashboard")

# 🔍 **Filters Section**
text("## 🌍 Filter Sales Data")

# 🌍 **Country Selection**
country_filter = selectbox(
    "🌍 Select a Country", 
    df["Country"].unique().tolist(), 
    default=df["Country"].unique()[0]
)

# 🍫 **Chocolate Product Selection**
product_filter = selectbox(
    "🍫 Filter by Chocolate Product",
    ["All Products"] + df["Product"].unique().tolist(),
    default="All Products"
)

# 🔽 **Sales Filter (Slider)**
min_sales = slider("📊 Minimum Sales Amount", min_val=int(df["Amount"].min()), max_val=int(df["Amount"].max()), default=int(df["Amount"].mean()))

# ✅ **Apply Filters**
filtered_df = df[(df["Country"] == country_filter) & (df["Amount"] >= min_sales)]
if product_filter != "All Products":
    filtered_df = filtered_df[filtered_df["Product"] == product_filter]

# ✅ **Checkbox for displaying all data**
show_all_data = checkbox("Show all data for selected country", default=False)

# 📋 **Filtered Table (Show 10 rows by default, all rows if checkbox checked)**
if show_all_data:
    table(filtered_df, title="📊 Complete Sales Data")
else:
    table(filtered_df.head(10), title="📊 Filtered Sales Data (Showing 10 Rows)")

# 📈 **Sales Trend Over Time**
fig_sales = px.line(
    df, x="Date_str", y="Amount", color="Country", 
    markers=True, title="Sales Over Time",
    labels={"Amount": "Sales Amount", "Date_str": "Date"}
)
fig_sales.update_layout(title_font=dict(size=22, family="Arial, sans-serif"))
plotly(fig_sales)

# 🎨 **Sales Distribution by Country (Histogram)**
fig_hist = px.histogram(
    df, x="Amount", color="Country", 
    nbins=30, title="Sales Distribution Analysis",
    labels={"Amount": "Sales Amount", "count": "Frequency"},
    barmode="overlay"
)
fig_hist.update_layout(
    xaxis_title="Sales Amount",
    yaxis_title="Frequency",
    legend_title="Country",
    template="plotly_white",
    plot_bgcolor="rgba(255, 255, 255, 1)",
    paper_bgcolor="rgba(245, 245, 245, 1)",
    font=dict(size=16, family="Arial, sans-serif"),
    title_font=dict(size=22, family="Arial, sans-serif"),
    margin=dict(l=40, r=40, t=40, b=40)
)
plotly(fig_hist)

# 🥧 **Sales Distribution by Country (Pie Chart)**
fig_pie = px.pie(
    df, names="Country", values="Amount", 
    title="Sales Distribution by Country",
    labels={"Amount": "Total Sales"}
)
fig_pie.update_layout(
    legend_title="Country",
    font=dict(size=16),
    title_font=dict(size=22, family="Arial, sans-serif")
)
plotly(fig_pie)

# ✅ **Footer**
text("🚀 **Powered by Preswald!**")
