import pandas as pd
import plotly.express as px

from preswald import plotly, text


# 1. Dashboard Title and Description
text("# Real Estate Data Analysis in India")
text("Exploring property prices, features, and market insights")


# Read and Preprocess the Dataset
def preprocess_data(df):
    # Function to convert price to float (in Crores)
    def convert_price(price_str):
        # Remove currency symbol
        price_str = price_str.replace("₹", "").strip()

        # Convert to float based on unit
        if "Cr" in price_str:
            # Convert Crores directly
            return float(price_str.replace(" Cr", ""))
        elif "L" in price_str:
            # Convert Lakhs to Crores (1 Crore = 100 Lakhs)
            return float(price_str.replace(" L", "")) / 100
        else:
            # If no unit, assume it's already in Crores
            return float(price_str)

    # Clean Price column
    df["Price"] = df["Price"].apply(convert_price)

    # Clean Total Area and Price per SQFT
    df["Total_Area"] = pd.to_numeric(df["Total_Area"], errors="coerce")
    df["Price_per_SQFT"] = pd.to_numeric(df["Price_per_SQFT"], errors="coerce")

    # Extract property type from Property Title
    df["Property_Type"] = df["Property Title"].str.extract(
        r"(\d+ BHK \w+)", expand=False
    )
    df["Property_Type"] = df["Property_Type"].fillna("Other")

    # Convert Balcony to boolean
    df["Balcony"] = df["Balcony"].map({"Yes": True, "No": False})

    return df


# Read the dataset
df = pd.read_csv("https://preswald.s3.us-east-1.amazonaws.com/real_estate.csv")
df = preprocess_data(df)

# 2. Price Distribution by Property Type
text("## Price Distribution by Property Type")
fig1 = px.box(
    df,
    x="Property_Type",
    y="Price",
    title="Price Distribution Across Property Types",
    color="Property_Type",
    labels={"Property_Type": "Property Type", "Price": "Price (in Crores)"},
)
fig1.update_layout(
    xaxis_title="Property Type", yaxis_title="Price (in Crores)", showlegend=False
)
plotly(fig1)

# 3. Price per SQFT vs Total Area Scatter Plot
text("## Price per SQFT vs Total Area")
fig2 = px.scatter(
    df,
    x="Total_Area",
    y="Price_per_SQFT",
    color="Price",
    size="Price",
    hover_data=["Location", "Property Title"],
    title="Relationship between Area and Price per SQFT",
    labels={
        "Total_Area": "Total Area (sq ft)",
        "Price_per_SQFT": "Price per SQFT",
        "Price": "Total Price (Crores)",
    },
)
plotly(fig2)

# 4. Location-wise Price Distribution
text("## Price Distribution by Top Locations")
# Limit to top 10 locations
top_locations = df["Location"].value_counts().nlargest(10).index
df_filtered = df[df["Location"].isin(top_locations)]

fig3 = px.box(
    df_filtered,
    x="Location",
    y="Price",
    title="Price Distribution in Top 10 Locations",
    color="Location",
)
fig3.update_layout(
    xaxis_title="Location", yaxis_title="Price (in Crores)", xaxis_tickangle=45
)
plotly(fig3)

# 5. Correlation Heatmap
text("## Correlation between Numeric Features")
# Select numeric columns
numeric_cols = ["Price", "Total_Area", "Price_per_SQFT", "Baths"]
corr_matrix = df[numeric_cols].corr()

fig4 = px.imshow(
    corr_matrix,
    text_auto=True,
    title="Correlation Heatmap of Numeric Features",
    color_continuous_scale="RdBu_r",
)
plotly(fig4)

# 6. Balcony vs No Balcony Price Comparison
text("## Price Comparison: Balcony vs No Balcony")
fig5 = px.box(
    df,
    x="Balcony",
    y="Price",
    title="Price Distribution: Properties with and without Balcony",
    color="Balcony",
)
fig5.update_layout(xaxis_title="Balcony Available", yaxis_title="Price (in Crores)")
plotly(fig5)

# 7. Number of Bathrooms vs Price
text("## Price Distribution by Number of Bathrooms")
fig6 = px.box(
    df,
    x="Baths",
    y="Price",
    title="Price Distribution by Number of Bathrooms",
    color="Baths",
)
fig6.update_layout(xaxis_title="Number of Bathrooms", yaxis_title="Price (in Crores)")
plotly(fig6)

# Additional insights text
text("## Key Insights")
text("""
- Property prices vary significantly across different types and locations
- There's a correlation between total area and price per SQFT
- Locations play a crucial role in determining property prices
- Presence of a balcony and number of bathrooms impact property valuation
""")
