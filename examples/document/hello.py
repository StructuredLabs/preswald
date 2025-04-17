# import fastplotlib as fpl
# import imageio.v3 as iio
# import numpy as np
import plotly.express as px

from preswald import (
    document,
    get_df,
    plotly,
    sidebar,
    text,
)


sidebar()


# 2. Histogram of Sepal Length
text(
    "## Iris Flower Classification Research Paper \n This research paper discusses the seminal work on iris flower classification, including Fisher's original 1936 paper that introduced this famous dataset for pattern recognition and machine learning."
)

document("sample.pdf", "Original Research Paper")

text(
    "## Visualizing the Dataset Features \n Below we can see a scatter plot visualization of two key features used in iris classification: sepal length vs sepal width. The clear clustering shows why this dataset became a standard test case for machine learning algorithms."
)

df = get_df("iris_csv")

fig = px.scatter(df, x="sepal.length", y="sepal.width", color="variety")

plotly(fig)
