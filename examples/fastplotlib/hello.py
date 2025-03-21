import fastplotlib as fpl
import numpy as np

from preswald import connect, fastplotlib, get_df, sidebar, text


# Load the CSV
connect()  # Load in all sources, which by default is the iris_csv
df = get_df("iris_csv")

sidebar(defaultopen=True)
text("# Fastplotlib Examples")

# Line Plot
text("## Line Plot")
x = np.linspace(-1, 10, 100)
y = np.sin(x)
sine = np.column_stack([x, y])
fig = fpl.Figure(size=(700, 560), canvas="offscreen")
fig[0, 0].add_line(data=sine, colors="w")
fastplotlib(fig)

# Line Plot ColorMap
text("## Line Plot ColorMap")
fig = fpl.Figure(size=(700, 560), canvas="offscreen")
xs = np.linspace(-10, 10, 100)
ys = np.sin(xs)
sine = np.dstack([xs, ys])[0]
ys = np.cos(xs) - 5
cosine = np.dstack([xs, ys])[0]
# cmap_transform from an array, so the colors on the sine line will be based on the sine y-values
sine_graphic = fig[0, 0].add_line(
    data=sine, thickness=10, cmap="plasma", cmap_transform=sine[:, 1]
)
# qualitative colormaps, useful for cluster labels or other types of categorical labels
labels = [0] * 25 + [5] * 10 + [1] * 35 + [2] * 30
cosine_graphic = fig[0, 0].add_line(
    data=cosine, thickness=10, cmap="tab10", cmap_transform=labels
)
fastplotlib(fig)

# Scatter Plot
text("## Scatter Plot")
x = df["sepal.length"].tolist()
y = df["petal.width"].tolist()
variety = df["variety"].tolist()
data = np.column_stack((x, y))
fig = fpl.Figure(size=(700, 560), canvas="offscreen")
color_map = {"Setosa": "yellow", "Versicolor": "cyan", "Virginica": "magenta"}
colors = [color_map[v] for v in variety]
scatter = fig[0, 0].add_scatter(data=data, sizes=4, colors=colors)
fastplotlib(fig)
