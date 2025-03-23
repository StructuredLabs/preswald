import plotly.express as px

from preswald import connect, get_df, plotly, separator, slider, table, text


# Load the CSV
connect()  # load the data source as specified in preswald.toml

# Two datasets are included, related to red and white vinho verde wine samples,
# from the north of Portugal. The goal is to model wine quality based on
# physicochemical tests (see [Cortez et al., 2009],
# http://www3.dsi.uminho.pt/pcortez/wine/).


# Create the data frame
full_df = get_df("winequality_csv")
"""
Column names:

fixed acidity,
volatile acidity,
citric acid,
residual sugar,
chlorides,
free sulfur dioxide,
total sulfur dioxide,
density,
pH,
sulphates,
alcohol,
quality,
color,
"""

# Create a data frame filtered to red wine only
red_df = full_df[full_df["color"] == "red"]


# Report Title
text("# Characteristics and Quality of Wine")
text(
    "This example uses measured characteristics of wine. "
    "Data includes chlorides, sugars, density, alcohol, and other attributes."
)

# Quality Slider
quality = slider(
    "Wine quality is measured on a scale from 0-10. Use this slider"
    " to change the minimum quality included in the next 3 figures.",
    min_val=0,
    max_val=10,
    default=1,
    size=4,
)
qual_full_df = full_df[full_df["quality"] >= quality]

fig1 = px.scatter(
    qual_full_df,
    x="chlorides",
    y="sulphates",
    title="Sulphates and Chlorides",
    color="color",
    labels={"red": "Red Wine", "white": "White Wine"},
)


# Sugar

fig2 = px.box(
    qual_full_df,
    y="residual sugar",
    x="color",
    title="Residual Sugar",
    labels={"red": "Red Wine", "white": "White Wine"},
)
fig2.update_layout(template="plotly_white")

# Density

fig3 = px.histogram(
    qual_full_df[qual_full_df["density"] <= 1.004],  # rid worst outliers
    x="density",
    color="color",
    title="Density",
    labels={"red": "Red Wine", "white": "White Wine"},
)


# Display the plots
plotly(fig1)
plotly(fig2)
plotly(fig3)

separator()
# White wine section
text("### White Wine")
text("Here is there one might put astonishing insights about **white wine**")

# Create a data frame filtered to white wine only
white_df = full_df[full_df["color"] == "white"]

# Create Sulfur Dioxide and Sugar plot

fig4 = px.scatter(
    white_df,
    x="total sulfur dioxide",
    y="residual sugar",
    color="quality",
    title="White Wine Total Sulfur Dioxide vs Residual Sugar, by Quality",
    category_orders={"quality": [0, 1, 2, 4, 5, 6, 7, 8, 9, 10]},
)
# Display the plot
plotly(fig4)


separator()
# Red wine section
text("## Red Wine")
text("Here is there one might put astonishing insights about **red wine**")

# Create the data frame as a subset of combined data
red_df = full_df[full_df["color"] == "red"]

# Create Sulfur Dioxide and Sugar plot

fig5 = px.scatter(
    red_df,
    x="total sulfur dioxide",
    y="residual sugar",
    color="quality",
    title="Red Wine Total Sulfur Dioxide vs Residual Sugar, by Quality",
)
# Display the plot
plotly(fig5)

text("## The Data")
text(
    "This data set is available from http://www3.dsi.uminho.pt/pcortez/wine/."
    " The original data is separated into red and white files. "
    "For this visualization they have been combined into a "
    "single dataset and given an additional `color` column."
)
text("Below is a random 10 row sample from the 6k+ combined data set")

sampled_df = full_df.sample(10)
# Show the sampled data
table(sampled_df)
