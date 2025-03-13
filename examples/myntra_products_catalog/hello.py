from preswald import text, plotly, connect, get_df, table,separator,slider, selectbox
import pandas as pd
import plotly.express as px
  

# separator()
text("# Myntra Interactive Product Dashboard 🛍️")

# Load the dataset
connect()
df = get_df("myntra_products_catalog")

# Drop missing values for important columns
df = df.dropna(subset=["ProductBrand", "PrimaryColor", "Gender", "Price (INR)"])

separator()

# 🛍️ **1. Personalized Product Finder**
text("## 🔍 Find Your Perfect Product")

# Brand Selection
brands = ["All"] + sorted(df["ProductBrand"].unique().tolist())
selected_brand = selectbox("Choose a Brand", brands, default="All")


valid_genders = ["Men", "Women", "Unisex"]
genders = ["All"] + [g for g in df["Gender"].unique() if g in valid_genders]
selected_gender = selectbox("Choose Gender", genders, default="All")

# Color Selection
colors = ["All"] + sorted(df["PrimaryColor"].unique().tolist())
selected_color = selectbox("Choose a Color", colors, default="All")


min_price, max_price = int(df["Price (INR)"].min()), int(df["Price (INR)"].max())

min_selected_price = slider(
    "Select Minimum Price",
    min_val=min_price,
    max_val=max_price,
    step=5000,
    default=min_price
)

max_selected_price = slider(
    "Select Maximum Price",
    min_val=min_price,
    max_val=max_price,
    step=5000,
    default=max_price
)


if min_selected_price > max_selected_price:
    min_selected_price, max_selected_price = max_selected_price, min_selected_price


filtered_df = df.copy()

if selected_brand != "All":
    filtered_df = filtered_df[filtered_df["ProductBrand"] == selected_brand]

if selected_gender != "All":
    filtered_df = filtered_df[filtered_df["Gender"] == selected_gender]

if selected_color != "All":
    filtered_df = filtered_df[filtered_df["PrimaryColor"] == selected_color]

filtered_df = filtered_df[filtered_df["Price (INR)"].between(min_selected_price, max_selected_price)]

text("### Filtered Results:")

if not filtered_df.empty:
    table(filtered_df)  
else:
    text("⚠️ No products match your filters. Try adjusting the options.")

separator()