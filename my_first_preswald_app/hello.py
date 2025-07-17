import pandas as pd
import plotly.express as px
from preswald import text, connect, slider, selectbox, plotly
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Initialize preswald
    connect()

    # Title
    text("# 📈 Superstore Sales & Profit Dashboard")

    # Load and preprocess
    df = pd.read_csv("data/my_sample_superstore.csv")
    print("Initial DataFrame shape:", df.shape)
    print("Columns:", df.columns.tolist())

    df["Order Date"]     = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df["Profit Margin"]  = df["Profit"] / df["Sales"]

    # State name to abbreviation mapping
    state_abbrev = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
        'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
        'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
        'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
    }

    # Convert state names to abbreviations
    print("\nUnique states before mapping:", df['State'].unique())
    df['State_Code'] = df['State'].map(state_abbrev)
    print("Unique state codes after mapping:", df['State_Code'].unique())

    # Sidebar widgets
    min_sales   = slider(
        "Minimum Sales Filter",
        min_val=0,
        max_val=int(df["Sales"].max()),
        default=0
    )
    segment_sel = selectbox(
        "Choose Segment",
        options=sorted(df["Segment"].unique().tolist()),
        default="Consumer"
    )

    # Apply filters
    df = df[(df["Sales"] >= min_sales) & (df["Segment"] == segment_sel)]
    print("\nDataFrame shape after filtering:", df.shape)

    # 1. Sales vs. Profit by Category
    text("## 1. Sales & Profit by Category")
    cat_stats = df.groupby("Category", as_index=False).agg(
        Total_Sales = ("Sales", "sum"),
        Total_Profit = ("Profit", "sum")
    )
    fig1 = px.bar(
        cat_stats,
        x="Category",
        y=["Total_Sales", "Total_Profit"],
        barmode="group",
        title="Sales and Profit by Category",
        labels={"value": "USD", "variable": "Measure"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig1.update_layout(template="plotly_white")
    plotly(fig1)

    # 2. Average Profit Margin by Region
    text("## 2. Average Profit Margin by Region")
    region_stats = df.groupby("Region", as_index=False)["Profit Margin"]\
                     .mean().rename(columns={"Profit Margin": "Avg_Profit_Margin"})
    fig2 = px.bar(
        region_stats,
        x="Region",
        y="Avg_Profit_Margin",
        title="Average Profit Margin by Region",
        labels={"Avg_Profit_Margin": "Profit Margin"},
        color="Avg_Profit_Margin",
        color_continuous_scale="Viridis"
    )
    fig2.update_layout(template="plotly_white")
    plotly(fig2)

    # 3. Segment-Specific Profit Margin by Category
    text(f"## 3. Profit Margin by Category: {segment_sel}")
    seg_cat = df.groupby("Category", as_index=False)["Profit Margin"]\
                .mean().rename(columns={"Profit Margin": "Profit_Margin"})
    fig3 = px.bar(
        seg_cat,
        x="Category",
        y="Profit_Margin",
        title=f"{segment_sel} Segment: Profit Margin by Category",
        labels={"Profit_Margin": "Profit Margin"},
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig3.update_layout(template="plotly_white")
    plotly(fig3)

    # 4. Total Sales by State (USA Map)
    text("## 4. Total Sales by State (USA)")
    state_sales = df.groupby("State_Code", as_index=False)["Sales"].sum()
    print("\nState sales data:")
    print(state_sales)
    fig4 = px.choropleth(
        state_sales,
        locations="State_Code",
        locationmode="USA-states",
        color="Sales",
        scope="usa",
        title="Total Sales by State",
        labels={"Sales": "Total Sales"},
        color_continuous_scale="Viridis"
    )
    fig4.update_layout(template="plotly_white")
    plotly(fig4)

except Exception as e:
    logger.error(f"Error in main function: {e}")