import fastplotlib as fpl
import imageio.v3 as iio
import numpy as np
import plotly.express as px

from preswald import (
    chat,
    connect,
    fastplotlib,
    get_df,
    plotly,
    sidebar,
    table,
    text,
)
from preswald.engine.service import PreswaldService


service = service = PreswaldService.get_instance()

# Report Title
text(
    "# Iris Data Viz with Preswald \n This report provides a visual analysis of the famous Iris dataset. Each plot explores different characteristics of the iris flowers across three species: Setosa, Versicolor, and Virginica."
)

# Load the CSV
connect()  # Load in all sources, which by default is the iris_csv
df = get_df("iris_csv")

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

# 6. Fastplotlib Examples

# Retrieve client_id from component state
client_id = service.get_component_state("client_id")

sidebar(defaultopen=True)
text("# Fastplotlib Examples")

# 6.1. Simple Image Plot
text("## Simple Image Plot")
fig = fpl.Figure(size=(700, 560), canvas="offscreen")
fig._client_id = client_id
fig._label = "Simple Image Plot"
data = iio.imread("images/logo.png")
fig[0, 0].add_image(data)
fastplotlib(fig)

# 6.2. Line Plot
text("## Line Plot")
x = np.linspace(-1, 10, 100)
y = np.sin(x)
sine = np.column_stack([x, y])
fig = fpl.Figure(size=(700, 560), canvas="offscreen")
fig._client_id = client_id
fig._label = "Line Plot"
fig[0, 0].add_line(data=sine, colors="w")
fastplotlib(fig)

# 6.3. Line Plot with Color Maps
text("## Line Plot ColorMap")
fig = fpl.Figure(size=(700, 560), canvas="offscreen")
fig._client_id = client_id
fig._label = "Line Plot Color Map"
xs = np.linspace(-10, 10, 100)
ys = np.sin(xs)
sine = np.dstack([xs, ys])[0]
ys = np.cos(xs) - 5
cosine = np.dstack([xs, ys])[0]

sine_graphic = fig[0, 0].add_line(
    data=sine, thickness=10, cmap="plasma", cmap_transform=sine[:, 1]
)
labels = [0] * 25 + [5] * 10 + [1] * 35 + [2] * 30
cosine_graphic = fig[0, 0].add_line(
    data=cosine, thickness=10, cmap="tab10", cmap_transform=labels
)
fastplotlib(fig)

# 6.4. Scatter Plot from Iris dataset
text("## Scatter Plot")
x = df["sepal.length"].tolist()
y = df["petal.width"].tolist()
variety = df["variety"].tolist()
data = np.column_stack((x, y))
color_map = {"Setosa": "yellow", "Versicolor": "cyan", "Virginica": "magenta"}
colors = [color_map[v] for v in variety]

fig = fpl.Figure(size=(700, 560), canvas="offscreen")
fig._client_id = client_id
fig._label = "Scatter Plot"
fig[0, 0].add_scatter(data=data, sizes=4, colors=colors)
fastplotlib(fig)

# Show the first 10 rows of the dataset
text(
    "## Sample of the Iris Dataset \n Below is a preview of the first 10 rows of the dataset, showing key measurements for each iris species."
)
table(df, limit=10)

# Add an interactive chat interface
text(
    "## Interactive Chat Interface\nUse this chat interface to ask questions about the iris dataset analysis. You can inquire about specific patterns, request explanations of the visualizations, or ask for additional insights."
)

chat("iris_csv")
