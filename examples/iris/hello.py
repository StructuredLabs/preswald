import plotly.express as px

from preswald import connect, get_df, plotly, sidebar, table, text


# Report Title
text(
    "# Iris Data Viz with Preswald \n This report provides a visual analysis of the famous Iris dataset. Each plot explores different characteristics of the iris flowers across three species: Setosa, Versicolor, and Virginica."
)

# Load the CSV
connect()  # Load in all sources, which by default is the iris_csv
df = get_df("iris_csv")

sidebar(defaultopen=True)

# 1. Scatter plot - Sepal Length vs Sepal Width
text(
    "## Sepal Length vs Sepal Width \n This scatter plot shows the relationship between sepal length and sepal width for different iris species. We can see that Setosa is well-separated from the other two species, while Versicolor and Virginica show some overlap."
)
fig1 = px.scatter(
    df,
    x="sepal.length",
    y="sepal.width",
    color="variety",
    title="Sepal Length vs Sepal Width",
    labels={"sepal.length": "Sepal Length", "sepal.width": "Sepal Width"},
)
fig1.update_layout(template="plotly_white")
plotly(fig1)

# 2. Histogram of Sepal Length
text(
    "## Distribution of Sepal Length \n This histogram displays the distribution of sepal lengths across the three iris species. Setosa tends to have shorter sepals, while Virginica generally has longer sepals."
)
fig3 = px.histogram(
    df, x="sepal.length", color="variety", title="Distribution of Sepal Length"
)
fig3.update_layout(template="plotly_white")
plotly(fig3)

# 3. Box plot of Sepal Width by Species
text(
    "## Sepal Width Distribution by Species \n This box plot shows the spread of sepal widths for each iris species. Setosa generally has wider sepals, while Versicolor and Virginica have a more similar range of values."
)
fig5 = px.box(
    df,
    x="variety",
    y="sepal.width",
    color="variety",
    title="Sepal Width Distribution by Species",
)
fig5.update_layout(template="plotly_white")
plotly(fig5)

# 4. Violin plot of Sepal Length by Species
text(
    "## Sepal Length Distribution by Species \n The violin plot provides a better understanding of the distribution of sepal lengths within each species. We can see the density of values and how they vary across species."
)
fig7 = px.violin(
    df,
    x="variety",
    y="sepal.length",
    color="variety",
    title="Sepal Length Distribution by Species",
)
fig7.update_layout(template="plotly_white")
plotly(fig7)

# 5. Density contour plot - Sepal Length vs Petal Length
text(
    "## Density Contour: Sepal Length vs Petal Length \n This density contour plot illustrates the relationship between sepal length and petal length. It highlights where the highest concentrations of data points occur for each species."
)
fig10 = px.density_contour(
    df,
    x="sepal.length",
    y="petal.length",
    color="variety",
    title="Density Contour of Sepal Length vs Petal Length",
)
fig10.update_layout(template="plotly_white")
plotly(fig10)

# Show the first 10 rows of the dataset
text(
    "## Sample of the Iris Dataset \n Below is a preview of the first 10 rows of the dataset, showing key measurements for each iris species."
)
table(df, limit=10)
