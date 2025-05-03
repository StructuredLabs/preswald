from preswald import connect, get_df, plotly, table, text, slider
import plotly.express as px
import plotly.graph_objects as go

# Step 1: Initialize connection and load dataset
connect()
df = get_df("sample_csv")

# Debugging: Check the structure of df
print(type(df))  # Should be a pandas DataFrame
print(df.head())  # Preview first few rows
print(df.columns)  # Check column names

# Ensure correct column names
expected_columns = {"sepal.length", "sepal.width", "petal.length", "variety"}
actual_columns = set(df.columns)

if not expected_columns.issubset(actual_columns):
    raise ValueError(f"Expected columns {expected_columns}, but found {actual_columns}")

# Step 2: App title and description
text("# Comprehensive Iris Dataset Analysis")
text(
    "This app provides an in-depth analysis of the Iris dataset, including scatter plots, histograms, box plots, violin plots, and more. Explore the relationships and distributions of sepal and petal measurements across the three iris species: Setosa, Versicolor, and Virginica."
)

# Step 3: Scatter plot - Sepal Length vs Sepal Width
text(
    "## Sepal Length vs Sepal Width \n This scatter plot shows the relationship between sepal length and sepal width for each species."
)
fig1 = px.scatter(
    data_frame=df,
    x="sepal.length",
    y="sepal.width",
    color="variety",
    title="Sepal Length vs Sepal Width",
    labels={"sepal.length": "Sepal Length (cm)", "sepal.width": "Sepal Width (cm)"},
)
plotly(fig1)

# Step 4: Histogram - Distribution of Petal Length
text(
    "## Distribution of Petal Length \n This histogram displays the distribution of petal lengths across the three species."
)
fig2 = px.histogram(
    data_frame=df,
    x="petal.length",
    color="variety",
    title="Distribution of Petal Length",
    labels={"petal.length": "Petal Length (cm)"},
)
plotly(fig2)

# Step 5: Box plot - Sepal Width by Species
text(
    "## Sepal Width Distribution by Species \n This box plot compares the spread of sepal widths for each species."
)
fig3 = px.box(
    data_frame=df,
    x="variety",
    y="sepal.width",
    color="variety",
    title="Sepal Width Distribution by Species",
    labels={"sepal.width": "Sepal Width (cm)"},
)
plotly(fig3)

# Step 6: Violin plot - Petal Length by Species
text(
    "## Petal Length Distribution by Species \n This violin plot provides a detailed view of the distribution of petal lengths within each species."
)
fig4 = px.violin(
    data_frame=df,
    x="variety",
    y="petal.length",
    color="variety",
    title="Petal Length Distribution by Species",
    labels={"petal.length": "Petal Length (cm)"},
)
plotly(fig4)

# Step 7: Density heatmap - Sepal Length vs Petal Length
text(
    "## Density Heatmap: Sepal Length vs Petal Length \n This heatmap shows the density of data points for sepal length and petal length."
)
fig5 = px.density_heatmap(
    data_frame=df,
    x="sepal.length",
    y="petal.length",
    facet_col="variety",
    title="Density Heatmap of Sepal Length vs Petal Length",
    labels={"sepal.length": "Sepal Length (cm)", "petal.length": "Petal Length (cm)"},
)
plotly(fig5)

# Step 8: Interactive scatter plot with slider
text(
    "## Interactive Scatter Plot: Sepal Length vs Petal Length \n Use the slider to filter data points based on sepal width."
)
sepal_width_threshold = slider("Sepal Width Threshold", min_val=2.0, max_val=4.5, default=3.0)

# Ensure filtering is valid
if "sepal.width" in df.columns:
    filtered_df = df[df["sepal.width"] > sepal_width_threshold]
else:
    filtered_df = df  # Fallback if column name is incorrect

fig6 = px.scatter(
    data_frame=filtered_df,
    x="sepal.length",
    y="petal.length",
    color="variety",
    title=f"Sepal Length vs Petal Length (Sepal Width > {sepal_width_threshold})",
    labels={"sepal.length": "Sepal Length (cm)", "petal.length": "Petal Length (cm)"},
)
plotly(fig6)

# Step 9: 3D Scatter plot - Sepal Length, Sepal Width, Petal Length
text(
    "## 3D Scatter Plot: Sepal Length, Sepal Width, and Petal Length \n This 3D scatter plot visualizes the relationship between sepal length, sepal width, and petal length for each species."
)
fig7 = px.scatter_3d(
    data_frame=df,
    x="sepal.length",
    y="sepal.width",
    z="petal.length",
    color="variety",
    title="3D Scatter Plot: Sepal Length, Sepal Width, and Petal Length",
    labels={
        "sepal.length": "Sepal Length (cm)",
        "sepal.width": "Sepal Width (cm)",
        "petal.length": "Petal Length (cm)",
    },
)
plotly(fig7)

# Step 10: Show the first 10 rows of the dataset
text(
    "## Preview of the Iris Dataset \n Below is a preview of the first 10 rows of the dataset."
)
table(df, limit=10)
