import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from preswald import (
    checkbox,
    connect,
    get_df,
    plotly,
    selectbox,
    slider,
    table,
    text,
)


text("# 🚗🚌🚘🚢 &nbsp;&nbsp; Automobile Sales &nbsp;&nbsp; 🚚✈🚐🚅")

# Load the CSV
connect()  # load in all sources, which by default is the sample_csv
df = get_df("auto_sales_data")

# Numerical features
df_num = df.select_dtypes(include=["float64", "int64"]).drop(columns=["ORDERNUMBER"])

# Categorical Features
df_cat = df.select_dtypes(include=["object"]).drop(
    columns=["PHONE", "ADDRESSLINE1", "CONTACTLASTNAME", "CONTACTFIRSTNAME"]
)

# Custom color palette

colors = ["#79a5db", "#e0a580", "#6fab90", "#896ca8", "#ADD8E6"]

# Descriptive Summary: Numeric features
summary = round(df_num.describe(), 2).T
table(summary, title="Descriptive Summary: Numeric features")

# Descriptive Summary: Categorical features
summary = df.select_dtypes(include=["object"]).describe().T
table(summary, title="Descriptive Summary: Categorical features")


# Univariate Analysis


def univariate_analysis_category(cols):
    text(f"### Distribution of {cols.title()}")
    value_counts = cat_columns[cols].value_counts()
    # Count plot
    fig = px.bar(
        value_counts,
        x=value_counts.index,
        y=value_counts.values,
        title=cols,
        labels={"x": "Categories", "y": "Count"},
        color_discrete_sequence=[colors],
    )
    fig.update_layout(width=700)
    fig.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#ffffff")
    plotly(fig)

    # Donut chart
    percentage = (value_counts / value_counts.sum()) * 100
    fig = px.pie(
        values=percentage,
        names=value_counts.index,
        labels={"names": "Categories", "values": "Percentage"},
        hole=0.5,
        color_discrete_sequence=colors,
    )
    fig.add_annotation(
        x=0.5,
        y=0.5,
        align="center",
        xref="paper",
        yref="paper",
        showarrow=False,
        font_size=15,
        text=f"{cols}",
    )
    fig.update_layout(legend={"x": 0.9, "y": 0.5})
    fig.update_layout(width=700)
    plotly(fig)


def univariate_analysis_numeric(column, nbins):
    # text(f"### Description of {column}")
    summary = (
        df_num[column]
        .describe()
        .reset_index()
        .rename(columns={"index": "Statistic", column: "Value"})
    )
    table(summary, title=f"Description of {column}")

    # Histogram with KDE
    hist_fig = px.histogram(
        df_num,
        x=column,
        nbins=nbins,
        marginal="violin",
        title=f"Histogram of {column}",
        color_discrete_sequence=["#79a5db"],
    )
    hist_fig.update_traces(marker={"line": {"color": "black", "width": 0.5}})
    plotly(hist_fig, size=0.5)

    # Boxplot
    box_fig = px.box(
        df_num,
        x=column,
        title=f"Boxplot of {column}",
        color_discrete_sequence=["#e0a580"],
    )
    plotly(box_fig, size=0.5)


cat_columns = df[["STATUS", "PRODUCTLINE", "DEALSIZE"]]
category_col = selectbox("Select Categorical Feature:", list(cat_columns.columns))
univariate_analysis_category(category_col)

# for x in cat_columns:
#     univariate_analysis_category(x)

bin_slider = slider("Select Number of Bins", min_val=5, max_val=50, step=5, default=20)

text("-" * 60)

for x in df_num:
    univariate_analysis_numeric(x, bin_slider)

text("-" * 60)

# Top 10 Counteries
country_counts = df["COUNTRY"].value_counts().nlargest(10)

# Funnel chart
fig = go.Figure(
    go.Funnel(
        y=country_counts.index,
        x=country_counts.values,
        textinfo="value",
        marker={"color": px.colors.sequential.Blues_r},
    )
)

fig.update_layout(
    # title="Top 10 Country Distribution",
    template="plotly_white"
)

text("### Top 10 Country Distribution")
plotly(fig)

# Top 10 Cities
city_counts = df["CITY"].value_counts().nlargest(10)

# Funnel chart
fig = go.Figure(
    go.Funnel(
        y=city_counts.index,
        x=city_counts.values,
        textinfo="value",
        marker={"color": px.colors.sequential.Blues_r},
    )
)

fig.update_layout(template="plotly_white")

text("### Top 10 City Distribution")
plotly(fig)

# Top 10 Customer
top10_customer = df.sort_values(by="SALES", ascending=False).head(5)
top10_customer = df["CUSTOMERNAME"].value_counts().nlargest(10)

# Funnel chart
fig = go.Figure(
    go.Funnel(
        y=top10_customer.index,
        x=top10_customer.values,
        textinfo="value",
        marker={"color": px.colors.sequential.Blues_r},
    )
)

fig.update_layout(template="plotly_white")

text("### Top 10 Customer Distribution")
plotly(fig)


# Bivariate Analysis
## Scatter plot
fig = px.scatter_matrix(
    df_num, dimensions=df_num.columns, title="Pairplot of Numeric Features"
)

# Corner plot by hiding upper diagonal
fig.update_traces(diagonal_visible=False)

plotly(fig)


corr = df_num.corr(method="pearson")
mask = np.triu(np.ones_like(corr, dtype=bool))

heatmap_fig = px.imshow(
    corr.mask(mask),
    text_auto=".2f",
    color_continuous_scale="Blues",
    labels={"x": "Features", "y": "Features", "color": "Correlation"},
)

heatmap_fig.update_layout(
    width=800, height=600, xaxis={"side": "top"}, yaxis={"autorange": "reversed"}
)

text("### Correlation Heatmap")
plotly(heatmap_fig)


# Sales Distribution in Product Line

text("### Sales Distribution in Deal Size")

fig = px.box(
    df, x="DEALSIZE", y="SALES", color="DEALSIZE", color_discrete_sequence=colors
)
fig.update_layout(
    xaxis_title="Deal Size",
    yaxis_title="Sales",
    height=500,
    width=800,
)

plotly(fig)


# Sales Distribution in Product Line
text("### Sales Distribution in Product Line")

fig = px.box(
    df,
    x="PRODUCTLINE",
    y="SALES",
    color="PRODUCTLINE",
    color_discrete_sequence=px.colors.sequential.Agsunset,
)
fig.update_layout(
    xaxis_title="Product Line",
    yaxis_title="Sales",
    height=500,
    width=800,
)

plotly(fig)

# Sales Trend
df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"], format="%d/%m/%Y", errors="coerce")
df["Year"] = df["ORDERDATE"].dt.year

# Aggregate sales by day
df_grouped = df.groupby(["ORDERDATE", "Year"])["SALES"].sum().reset_index()

# Convert ORDERDATE to string to avoid JSON serialization issues
df_grouped["ORDERDATE"] = df_grouped["ORDERDATE"].astype(str)


show_markers = checkbox("Enable markers?", default=False)

# Create a separate trace for each year
fig = px.line(
    df_grouped,
    x="ORDERDATE",
    y="SALES",
    color="Year",
    color_discrete_sequence=px.colors.sequential.Hot,
    markers=show_markers,
)

fig.update_traces(line={"width": 0.5}, marker={"size": 4})

fig.update_layout(
    xaxis_title="Year",
    yaxis_title="SALES",
    height=500,
    width=1000,
    autosize=True,
    margin={"l": 10, "r": 10, "t": 50, "b": 50},
    legend_title="Year",
)

text("### Sales Trend by Year")
plotly(fig)


# Multivariate Analysis

df["SALES (K)"] = df["SALES"] / 1000

fig = px.bar(
    df,
    x="PRODUCTLINE",
    y="SALES (K)",
    color="DEALSIZE",
    barmode="group",
    color_discrete_sequence=px.colors.qualitative.Set2,
)

# Remove individual segment labels
fig.update_traces(texttemplate="")

# Add total sales labels on top of each stack
df_grouped = df.groupby("PRODUCTLINE")["SALES (K)"].sum().reset_index()
for _, row in df_grouped.iterrows():
    fig.add_annotation(
        x=row["PRODUCTLINE"],
        y=row["SALES (K)"],
        text=f"{row['SALES (K)']:.1f}K",
        showarrow=False,
        font={"size": 10},
        yshift=5,
    )

fig.update_layout(
    xaxis_title="Product Line",
    yaxis_title="SALES (K)",
    legend_title="Deal Size",
    width=1000,
    height=500,
    margin={"l": 20, "r": 20, "t": 50, "b": 50},
    template="plotly_white",
)

text("### Comparison between Sales, Product Line & Deal Size")
plotly(fig)


# ORDERDATE datetime format
df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"], errors="coerce")

numeric_cols = df.select_dtypes(include=["number"])

# Resample and calculate mean only on numeric columns
df_resampled = (
    df.resample("ME", on="ORDERDATE")[numeric_cols.columns].mean().reset_index()
)

# Selling Price Difference
df_resampled["SELLING_PRICE_DIFF"] = df_resampled["PRICEEACH"] - df_resampled["MSRP"]

df_resampled["ORDERDATE"] = df_resampled["ORDERDATE"].astype(str)


fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=df_resampled["ORDERDATE"],
        y=df_resampled["PRICEEACH"],
        mode="lines",
        name="Price Each",
        line={"color": "blue"},
    )
)

# MSRP Line
fig.add_trace(
    go.Scatter(
        x=df_resampled["ORDERDATE"],
        y=df_resampled["MSRP"],
        mode="lines",
        name="MSRP",
        line={"color": "orange"},
    )
)

# Selling Price Difference Area Fill
fig.add_trace(
    go.Scatter(
        x=df_resampled["ORDERDATE"],
        y=df_resampled["SELLING_PRICE_DIFF"],
        fill="tozeroy",
        name="Selling Price Difference",
        line={"color": "red"},
        opacity=0.5,
    )
)

fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Values",
    width=1000,
    height=500,
    margin={"l": 20, "r": 20, "t": 50, "b": 50},
    legend_title="Legend",
)

text("### Trends of Price Each, MSRP, and Selling Price Difference")
plotly(fig)
