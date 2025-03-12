import plotly.express as px
from preswald import connect, get_df, plotly, table, text

# Report Title
text(
    "# Wine Quality Analysis with Preswald \n This report provides a visual analysis of wine quality dataset, exploring different characteristics that impact quality."
)

# Load the dataset
connect()  # Load all sources
wine_df = get_df("wine")

# 1. Scatter plot - Alcohol vs Quality
text(
    "## Alcohol Content vs Wine Quality \n This scatter plot shows the relationship between alcohol content and wine quality. Higher alcohol content often correlates with better quality."
)
fig1 = px.scatter(
    wine_df,
    x="alcohol",
    y="quality",
    color="quality",
    title="Alcohol Content vs Wine Quality",
    labels={"alcohol": "Alcohol Content", "quality": "Quality Rating"},
)
fig1.update_layout(template="plotly_white")
plotly(fig1)

# 2. Histogram of Alcohol Content
text(
    "## Distribution of Alcohol Content \n This histogram displays the distribution of alcohol content in the dataset, giving an overview of its variance."
)
fig2 = px.histogram(
    wine_df, x="alcohol", color="quality", title="Distribution of Alcohol Content"
)
fig2.update_layout(template="plotly_white")
plotly(fig2)

# 3. Box plot - pH Level by Wine Quality
text(
    "## pH Level Distribution by Wine Quality \n This box plot shows the spread of pH levels for different wine quality ratings."
)
fig3 = px.box(
    wine_df,
    x="quality",
    y="pH",
    color="quality",
    title="pH Level Distribution by Wine Quality",
)
fig3.update_layout(template="plotly_white")
plotly(fig3)

# 4. Violin plot - Sulphates by Quality
text(
    "## Sulphates Content Across Quality Ratings \n The violin plot provides insights into the distribution of sulphate levels and their effect on wine quality."
)
fig4 = px.violin(
    wine_df,
    x="quality",
    y="sulphates",
    color="quality",
    title="Sulphates Content by Wine Quality",
)
fig4.update_layout(template="plotly_white")
plotly(fig4)

# 5. Density contour plot - Fixed Acidity vs Citric Acid
text(
    "## Density Contour: Fixed Acidity vs Citric Acid \n This plot illustrates the density of data points based on fixed acidity and citric acid levels."
)
fig5 = px.density_contour(
    wine_df,
    x="fixed acidity",
    y="citric acid",
    color="quality",
    title="Density Contour of Fixed Acidity vs Citric Acid",
)
fig5.update_layout(template="plotly_white")
plotly(fig5)

# Show the first 10 rows of the dataset
text(
    "## Sample of the Wine Quality Dataset \n Below is a preview of the first 10 rows of the dataset, showing key chemical properties and wine quality ratings."
)
table(wine_df, limit=10)