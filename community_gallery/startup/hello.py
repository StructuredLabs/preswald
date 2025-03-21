import pandas as pd
import plotly.express as px

from preswald import connect, get_df, plotly, table, text


# print("Before to Preswald!")
text("# Welcome to creative startup analysis with Preswald!")
# print("Welcome to Preswald!")
text("This is my first PRESWALD app. 🎉")

# Load the CSV
print("Loading data...")
connect()  # load in all sources, which by default is the sample_csv
df = get_df("startup_data")

# Display the full dataset
text("## Full Dataset")
text("Below is the full dataset used for this analysis.")
table(df)

text("# Startup Data Analysis")

## 1. Scatter Plot: Funding Amount vs. Valuation
text("### Funding Amount vs. Valuation")
text(
    "This scatter plot visualizes the relationship between **Funding Amount** and **Valuation** for the startups. It helps us understand if higher funding correlates with higher valuation."
)
fig1 = px.scatter(
    df,
    x="Funding Amount (M USD)",
    y="Valuation (M USD)",
    hover_data=["Startup Name", "Industry", "Region"],
    title="Funding Amount vs. Valuation",
    labels={
        "Funding Amount (M USD)": "Funding Amount (Million USD)",
        "Valuation (M USD)": "Valuation (Million USD)",
    },
)
fig1.update_layout(template="plotly_white")
plotly(fig1)

## 2. Bar Chart: Startup Count by Industry
text("### Startup Count by Industry")
text(
    "This bar chart shows the **number of startups** in each **Industry**. It helps us understand the distribution of startups across different sectors."
)
industry_counts = df["Industry"].value_counts().reset_index()
industry_counts.columns = ["Industry", "Count"]
fig2 = px.bar(
    industry_counts,
    x="Industry",
    y="Count",
    title="Startup Count by Industry",
    labels={"Industry": "Industry", "Count": "Number of Startups"},
)
fig2.update_layout(template="plotly_white")
plotly(fig2)

## 3. Scatter Plot: Revenue vs. Employees
text("### Revenue vs. Employees")
text(
    "This scatter plot explores the relationship between **Revenue** and **Employees**. It helps us understand if larger companies (in terms of employees) tend to generate more revenue."
)
fig3 = px.scatter(
    df,
    x="Employees",
    y="Revenue (M USD)",
    hover_data=["Startup Name", "Industry", "Region"],
    title="Revenue vs. Employees",
    labels={
        "Employees": "Number of Employees",
        "Revenue (M USD)": "Revenue (Million USD)",
    },
)
fig3.update_layout(template="plotly_white")
plotly(fig3)

text("### Valuation vs. Revenue")
text(
    "This scatter plot explores the relationship between **Valuation** and **Revenue**. It helps us understand if higher revenue correlates with higher valuations."
)
fig9 = px.scatter(
    df,
    x="Revenue (M USD)",
    y="Valuation (M USD)",
    hover_data=["Startup Name", "Industry", "Region"],
    title="Valuation vs. Revenue",
    labels={
        "Revenue (M USD)": "Revenue (Million USD)",
        "Valuation (M USD)": "Valuation (Million USD)",
    },
)
fig9.update_layout(template="plotly_white")
plotly(fig9)

## 4. Box Plot: Funding Amount by Region
text("### Funding Amount Distribution by Region")
text(
    "This box plot compares the **distribution of Funding Amount** across different **Regions**. It helps us identify regions with higher or lower funding levels and potential outliers."
)
fig4 = px.box(
    df,
    x="Region",
    y="Funding Amount (M USD)",
    color="Region",
    title="Funding Amount Distribution by Region",
    labels={
        "Region": "Region",
        "Funding Amount (M USD)": "Funding Amount (Million USD)",
    },
)
fig4.update_layout(template="plotly_white")
plotly(fig4)

## 5. Histogram: Distribution of Founding Year
text("### Distribution of Founding Year")
text(
    "This histogram shows the **distribution of Founding Year** for the startups. It helps us understand the historical trends in startup creation."
)
fig5 = px.histogram(
    df,
    x="Year Founded",
    title="Distribution of Founding Year",
    labels={"Year Founded": "Founding Year"},
)
fig5.update_layout(template="plotly_white")
plotly(fig5)

## 6. Violin Plot: Valuation by Industry
text("### Valuation Distribution by Industry")
text(
    "This violin plot provides a **detailed view of the Valuation distribution** within each **Industry**. The width of each shape indicates the density of valuations at different levels."
)
fig6 = px.violin(
    df,
    x="Industry",
    y="Valuation (M USD)",
    color="Industry",
    title="Valuation Distribution by Industry",
    labels={"Valuation (M USD)": "Valuation (Million USD)"},
    box=True,
)
fig6.update_layout(template="plotly_white")
plotly(fig6)

## 7. Bar Chart: Count of Startups by Exit Status
text("### Startup Count by Exit Status")
text(
    "This bar chart shows the **number of startups** for each **Exit Status**. It helps us understand the outcomes of the startups in the dataset."
)
exit_counts = df["Exit Status"].value_counts().reset_index()
exit_counts.columns = ["Exit Status", "Count"]
fig7 = px.bar(
    exit_counts,
    x="Exit Status",
    y="Count",
    title="Startup Count by Exit Status",
    labels={"Exit Status": "Exit Status", "Count": "Number of Startups"},
)
fig7.update_layout(template="plotly_white")
plotly(fig7)

## 8. Correlation Heatmap Between Features
text("### Feature Correlation Heatmap")
text(
    "This heatmap displays the **correlations between numerical features**. Strong positive or negative correlations can indicate relationships between variables."
)
corr_matrix = df[
    [
        "Funding Amount (M USD)",
        "Valuation (M USD)",
        "Revenue (M USD)",
        "Employees",
        "Year Founded",
        "Funding Rounds",
    ]
].corr()  # Selecting relevant numerical columns
fig8 = px.imshow(
    corr_matrix,
    text_auto=True,
    color_continuous_scale="viridis",
    title="Feature Correlation Heatmap",
)
plotly(fig8)

# Convert "Year Founded" to datetime objects (if needed)
df["Year Founded"] = pd.to_datetime(df["Year Founded"], format="%Y")

# Group by year and sum the funding amount
funding_by_year = (
    df.groupby(df["Year Founded"].dt.year)["Funding Amount (M USD)"].sum().reset_index()
)

# Create a bar chart
text("## Total Funding Amount per Year")
fig10 = px.bar(
    funding_by_year,
    x="Year Founded",
    y="Funding Amount (M USD)",
    title="Total Funding Amount per Year",
    labels={"Funding Amount (M USD)": "Funding Amount (Million USD)"},
)
plotly(fig10)

# general dataset info for basic analysis
# general dataset information
text("## General Dataset Information(Rough Analysis for Understanding)")
text(f"dataframe head {df.head()}")
text(f"dataframe tail {df.tail()}")
text(f"dataframe columns {df.columns}")
text(f"dataframe dtypes {df.dtypes}")
text(f"dataframe info {df.info()}")
text(f"dataframe na count {df.isna().sum()}")
