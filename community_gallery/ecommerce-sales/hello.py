import preswald as pw
import plotly.express as px
import pandas as pd

try:
    df_amazon = pd.read_csv("data/Amazon_Sale_Report.csv", dtype={"column_name": str}, low_memory=False)
    df_cloud = pd.read_csv("data/Cloud_Warehouse_Compersion_Chart.csv", dtype={"column_name": str}, low_memory=False)
    df_pl = pd.read_csv("data/P_L_March_2021.csv", dtype={"column_name": str}, low_memory=False)
    df_sale = pd.read_csv("data/Sale_Report.csv", dtype={"column_name": str}, low_memory=False)
    
except FileNotFoundError as e:
    pw.alert(f"⚠️ Error: {e}", level="critical")
    df_amazon = pd.DataFrame()
    df_cloud = pd.DataFrame()
    df_pl = pd.DataFrame()
    df_sale = pd.DataFrame()


pw.separator()
pw.text("## E-Commerce & Warehouse Overview Dashboard", size=24)
merged_sales_stock = df_amazon.merge(df_sale, left_on="SKU", right_on="SKU Code", how="left")

merged_prices = df_amazon.merge(df_pl, left_on="SKU", right_on="Sku", how="left")
top_skus = df_amazon.groupby("SKU")["Amount"].sum().reset_index()

pw.text("### 🏆 Top Product Categories by Sales", size=24)
pw.text("🚀 This chart highlights the product categories generating the highest revenue. "
        "Understanding which categories sell the most helps businesses focus on bestsellers, optimize stock levels, "
        "and plan future inventory effectively. Use these insights to boost profitability and streamline product strategy.")

pw.separator()

top_categories = df_amazon.groupby("Category")["Amount"].sum().reset_index()

fig1 = px.bar(
    top_categories,
    x="Category",
    y="Amount",
    color="Amount",
    text_auto=".2s",  # Show values inside bars
    labels={"Amount": "Total Sales (₹)", "Category": "Product Category"},
    height=400,
    width=1000
)

fig1.update_layout(
    xaxis_title="Product Category",
    yaxis_title="Total Sales Amount (₹)",
    font=dict(family="Arial", size=14),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=40, t=50, b=40),
    title_x=0.5,
    bargap=0.3
)

pw.plotly(fig1)

pw.separator()

pw.text("### 📦 Improved Stock Levels per Category", size=24)
pw.text("📊 This graph provides a clear view of stock availability across different product categories. "
        "Tracking stock levels ensures businesses can meet demand, prevent shortages, and avoid overstocking. "
        "Use this data to manage inventory efficiently and maintain a balanced supply chain.")

stock_by_category = df_sale.groupby("Category")["Stock"].sum().reset_index()

fig2 = px.sunburst(
    stock_by_category,
    path=["Category"],  # Define hierarchy (Only Category here)
    values="Stock",
    color="Stock",
    color_continuous_scale="Blues",
)

fig2.update_layout(
    title_x=0.5,
    margin=dict(l=40, r=40, t=50, b=40),
)

pw.plotly(fig2)

def clean_amazon_data(df):
    if df.empty:
        return df
    df["Date"] = pd.to_datetime(df["Date"], format="%m-%d-%y", errors="coerce").astype(str)

    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["ship-state"] = df["ship-state"].astype(str).str.strip().str.upper()
    df = df.dropna(subset=["Category", "SKU", "ship-state", "Amount"], how="any")
    return df

def clean_warehouse_data(df):
    if df.empty:
        return df
    # Example rename
    df.rename(columns={"Unnamed: 1": "Metric"}, inplace=True)
    return df

def clean_pl_data(df):
    if df.empty:
        return df
    numeric_cols = [
        "TP 1","TP 2","MRP Old","Final MRP Old",
        "Ajio MRP","Amazon MRP","Amazon FBA MRP",
        "Flipkart MRP","Limeroad MRP","Myntra MRP",
        "Paytm MRP","Snapdeal MRP"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Sku"])
    return df

def clean_sale_data(df):

    if df.empty:
        return df
    if "SKU Code" in df.columns:
        df.rename(columns={"SKU Code": "SKU"}, inplace=True)
    return df


df_amazon = clean_amazon_data(df_amazon)
df_cloud = clean_warehouse_data(df_cloud)
df_pl = clean_pl_data(df_pl)
df_sale = clean_sale_data(df_sale)
pw.separator()
pw.text("### Dashboard Controls", size=20)


data_options = ["Amazon Sale Report", "P&L March 2021", "Sale Report"]
dataset_choice = pw.selectbox("Select a primary dataset:", options=data_options)

pw.separator()



if dataset_choice == "Amazon Sale Report":
    if df_amazon.empty:
        pw.alert("🚨 Amazon Sale Report Data is empty!", level="critical")
    else:

        df_amz_filtered = df_amazon.copy()
        pw.text("### 📊 Amazon Sales Dashboard", size=28)
        ship_states = df_amazon["ship-state"].dropna().unique().tolist()
        categories = df_amazon["Category"].dropna().unique().tolist()
        selected_state = pw.selectbox("🌍 Filter by State:", options=["All"] + ship_states, size=0.5)
        selected_category = pw.selectbox("🛍️ Filter by Category:", options=["All"] + categories, size=0.5)
        df_filtered = df_amz_filtered.copy()
        if selected_state != "All":
            df_filtered = df_filtered[df_filtered["ship-state"] == selected_state]
        if selected_category != "All":
            df_filtered = df_filtered[df_filtered["Category"] == selected_category]
        total_orders = len(df_filtered["Order ID"].unique())
        total_sales = df_filtered["Amount"].sum(skipna=True)
        pw.text(f"**🛒 Total Orders:** {total_orders}", size=0.5)
        pw.text(f"**💰 Total Sales:** ₹{total_sales:,.2f}", size=0.5)

        pw.separator()
        
        if "Category" in df_filtered.columns:
            pw.text("### 🥇 Top 5 Categories by Sales", size=24)
            pw.text("💰 This visualization focuses on the five most profitable product categories. "
        "Knowing which categories generate the most revenue helps businesses prioritize top-performing products, "
        "align marketing strategies, and make data-driven decisions for future growth.")

            top_categories = df_filtered.groupby("Category")["Amount"].sum().nlargest(5).reset_index()

            fig2 = px.bar(
                top_categories,
                x="Category",
                y="Amount",
                color="Amount",
                text_auto=True,
                labels={"Amount": "Total Sales (₹)", "Category": "Product Category"},
                height=400,
                width=1000
            )

            fig2.update_layout(
                xaxis_title="Category",
                yaxis_title="Total Sales Amount (₹)",
                title_x=0.5,
                bargap=0.3
            )

            pw.plotly(fig2)

        pw.separator()

        if "Date" in df_filtered.columns:
            
            sales_by_date = df_filtered.groupby("Date")["Amount"].sum().reset_index()
            fig_line = px.line(sales_by_date, x="Date", y="Amount")
            pw.text("### 📅 Sales Over Time", size=24)
            pw.text("📈 Tracking sales performance over time helps businesses understand seasonal trends, "
        "identify peak sales periods, and anticipate fluctuations. "
        "By analyzing past trends, businesses can forecast demand, adjust pricing, and optimize sales strategies effectively.")


            fig_line.update_layout(
                xaxis_title="Date",
                yaxis_title="Total Sales Amount (₹)",
                title_x=0.5
            )

            pw.plotly(fig_line)

        pw.separator()

        if "ship-state" in df_filtered.columns and "Amount" in df_filtered.columns:
            df_filtered["ship-state"] = df_filtered["ship-state"].astype(str).str.strip().str.upper()
            state_sales = df_filtered.groupby("ship-state").agg({"Amount": "sum", "Order ID": "count"}).reset_index()
            state_sales.columns = ["State", "Total Sales", "Order Count"]
            pw.text("### 💰 Amount Spent by Each State", size=24)
            pw.text("🏙️ This graph shows which states contribute the most to total revenue. "
        "Understanding regional sales distribution allows businesses to target high-value locations, "
        "optimize logistics, and personalize marketing efforts for maximum impact.")

            fig3 = px.bar(
                state_sales,
                x="State",
                y="Total Sales",
                labels={"Total Sales": "Total Amount (₹)", "State": "State"},
                height=500,
                width=1100
            )

            fig3.add_trace(
                px.line(
                    state_sales,
                    x="State",
                    y="Order Count",
                    labels={"Order Count": "Number of Orders"},
                ).data[0]
            )

            fig3.update_layout(
                xaxis_title="State",
                yaxis_title="Total Sales (₹)",
                title_x=0.5,
                yaxis=dict(
                    tickmode="array",
                    tickvals=[0, 1000000, 2000000, 3000000, 4000000],  # 1M gaps
                    ticktext=["0", "1M", "2M", "3M", "4M"]
                ),
                yaxis2=dict(
                    overlaying="y",
                    side="right",
                    title="Number of Orders",
                    showgrid=False
                ),
                bargap=0.3
            )

            pw.plotly(fig3)

        pw.separator()
        if "Status" in df_filtered.columns:
            orders_by_status = df_filtered["Status"].value_counts().reset_index()
            orders_by_status.columns = ["Status", "Order Count"]
            pw.text("### 📦 Orders & Status Overview", size=24)
            pw.text("📊 This chart provides an overview of order statuses, including shipped, delivered, and canceled orders. "
        "Monitoring order distribution helps businesses improve fulfillment speed, reduce cancellations, "
        "and enhance customer experience by ensuring timely deliveries.")


            fig1 = px.bar(
                orders_by_status,
                y="Status",  
                x="Order Count",
                color="Order Count",
                text_auto=True,
                labels={"Order Count": "Total Orders", "Status": "Order Status"},
                height=400,
                width=1000,
                orientation="h" 
            )

            fig1.update_layout(
                xaxis_title="Number of Orders",
                yaxis_title="Order Status",
                title_x=0.5,
                bargap=0.3
            )

            pw.plotly(fig1)

        pw.separator()





elif dataset_choice == "P&L March 2021":
    if df_pl.empty:
        pw.alert("🚨 P&L March 2021 Data is empty!", level="critical")
    else:
        pw.text("### 📊 Pricing & Profitability Insights", size=24)
        
        pw.text("### 🛒 Price Distribution Across Marketplaces", size=24)
        pw.text("📊 Understanding how pricing varies across platforms like Amazon, Flipkart, and Myntra "
                "helps businesses set competitive pricing strategies. "
                "This visualization highlights pricing consistency and variations across different marketplaces.")

        if {"Amazon MRP", "Flipkart MRP", "Myntra MRP", "Snapdeal MRP", "Paytm MRP"}.issubset(df_pl.columns):
            fig1 = px.box(
                df_pl,
                y=["Amazon MRP", "Flipkart MRP", "Myntra MRP", "Snapdeal MRP", "Paytm MRP"],
                title="🛒 Price Distribution Across Marketplaces",
                labels={"value": "MRP Price (₹)", "variable": "Marketplace"},
                boxmode="group"
            )
            pw.plotly(fig1)


        pw.text("### 💰 Category-Wise Average MRP", size=24)
        pw.text("📊 This chart compares the average MRP across different product categories. "
                "Identifying which categories have the highest and lowest pricing can help businesses "
                "adjust pricing strategies and optimize product profitability.")

        if "Category" in df_pl.columns and "Final MRP Old" in df_pl.columns:
            df_category_avg = df_pl.groupby("Category")["Final MRP Old"].mean().reset_index()
            
            df_category_avg["Final MRP Old"] = df_category_avg["Final MRP Old"].round(2)

            fig2 = px.bar(
                df_category_avg,
                y="Category",
                x="Final MRP Old",
                title="💰 Category-Wise Average MRP",
                text_auto=True,  
                labels={"Final MRP Old": "Average MRP (₹)", "Category": "Product Category"},
                orientation="h", 
                height=500,
                width=1000
            )

            fig2.update_layout(
                xaxis_title="Average MRP (₹)",
                yaxis_title="Category",
                title_x=0.5,
                bargap=0.3
            )

            pw.plotly(fig2)

        pw.separator()


elif dataset_choice == "Sale Report":
    if df_sale.empty:
        pw.alert("🚨 Sale Report Data is empty!", level="critical")
    else:
        pw.text("### 📊 Inventory & Stock Insights", size=24)
        
        pw.text("### 📦 Total Stock by Category", size=24)
        pw.text("📊 This visualization highlights the total stock available for each category. "
                "It helps businesses identify product groups that are well-stocked versus those that need replenishment.")
        
        if "Category" in df_sale.columns and "Stock" in df_sale.columns:
            stock_by_cat = df_sale.groupby("Category")["Stock"].sum().reset_index()
            fig_stock = px.bar(
                stock_by_cat,
                x="Category",
                y="Stock",
                title="📦 Total Stock by Category",
                text_auto=True,  
                labels={"Stock": "Total Stock Available", "Category": "Product Category"},
                height=400,
                width=1000
            )
            pw.plotly(fig_stock)

        pw.text("### 📏 Stock Availability by Size", size=24)
        pw.text("📊 Understanding stock levels across different sizes helps businesses manage inventory effectively. "
                "This visualization highlights which sizes are overstocked or in short supply.")

        if "Size" in df_sale.columns and "Stock" in df_sale.columns:
            stock_by_size = df_sale.groupby("Size")["Stock"].sum().reset_index()
            fig_size = px.funnel(
                stock_by_size,
                x="Stock",
                y="Size",
                title="📏 Stock Availability by Size",
                labels={"Stock": "Stock Quantity", "Size": "Size"},
                height=400,
                width=1000
            )
            pw.plotly(fig_size)



        pw.text("### 🏷️ Stock Concentration by Design Number", size=24)
        pw.text("📌 This visualization shows which product designs hold the most stock. "
                "It helps businesses determine which designs are dominant in inventory.")

        if "Design No." in df_sale.columns and "Stock" in df_sale.columns:
            stock_by_design = df_sale.groupby("Design No.")["Stock"].sum().reset_index()
            fig_design = px.treemap(
                stock_by_design,
                path=["Design No."],
                values="Stock",
                title="🏷️ Stock Concentration by Design Number"
            )
            pw.plotly(fig_design)

        pw.separator()


pw.separator()
pw.text(f"**End of {dataset_choice}**", size=18)

