import plotly.express as px
import plotly.figure_factory as ff

from preswald import connect, get_df, plotly, table, text


# Title and Introduction
text("# 🐧 Exploring the Penguins Dataset with Preswald")
text(
    "This report provides a visual exploration of the Palmer Penguins dataset, which contains measurements of three penguin species: **Adelie, Chinstrap, and Gentoo**. "
    "The dataset includes information on their bill size, flipper length, body mass, and the island where they were found."
)

# Load the dataset
connect()  # Load in all sources, which by default includes 'penguins'
df = get_df("penguins_csv")

## 2. Histogram: Distribution of Flipper Length
text("### Distribution of Flipper Length")
text(
    "This histogram illustrates the **flipper length distribution** across different species. It helps us understand how flipper lengths vary within and between species."
)
fig2 = px.histogram(
    df,
    x="flipper_length_mm",
    color="species",
    title="Distribution of Flipper Length",
    labels={"flipper_length_mm": "Flipper Length (mm)"},
    barmode="overlay",
    opacity=0.7,
)
fig2.update_layout(template="plotly_white")
plotly(fig2)

## 3. Box Plot: Body Mass by Species
text("### Body Mass Distribution by Species")
text(
    "This box plot compares the **body mass distribution** across the three penguin species. It provides insights into weight variations and outliers in the dataset."
)
fig3 = px.box(
    df,
    x="species",
    y="body_mass_g",
    color="species",
    title="Body Mass Distribution by Species",
    labels={"body_mass_g": "Body Mass (g)", "species": "Penguin Species"},
)
fig3.update_layout(template="plotly_white")
plotly(fig3)

## 4. Scatter Plot: Bill Length vs. Bill Depth Colored by Sex
text("### Bill Length vs. Bill Depth (by Sex)")
text(
    "This scatter plot displays how **bill length and bill depth** differ between males and females within each species. The variation may be linked to dietary adaptations."
)
fig4 = px.scatter(
    df,
    x="bill_length_mm",
    y="bill_depth_mm",
    color="sex",
    symbol="species",
    title="Bill Length vs. Bill Depth (Colored by Sex)",
    labels={
        "bill_length_mm": "Bill Length (mm)",
        "bill_depth_mm": "Bill Depth (mm)",
        "sex": "Sex",
    },
)
fig4.update_traces(marker={"size": 10})
fig4.update_layout(template="plotly_white")
plotly(fig4)

## 5. Bar Plot: Count of Penguins by Island
text("### Penguin Population by Island")
text(
    "This bar plot shows the **number of penguins found on each island**. It helps us understand the habitat distribution of different species."
)
fig5 = px.bar(
    df,
    x="island",
    color="species",
    title="Penguin Count by Island",
    labels={"island": "Island", "species": "Species"},
    barmode="group",
)
fig5.update_layout(template="plotly_white")
plotly(fig5)

## 6. Pairplot Matrix for Key Features
text("### Pairplot Matrix for Key Features")
text(
    "The scatter matrix below visualizes **pairwise relationships between numerical features** such as bill length, bill depth, flipper length, and body mass."
)
fig6 = px.scatter_matrix(
    df,
    dimensions=["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"],
    color="species",
    title="Pairplot Matrix for Key Features",
)
fig6.update_layout(template="plotly_white")
plotly(fig6)

## 7. Violin Plot of Bill Length by Species
text("### Violin Plot: Bill Length by Species")
text(
    "This violin plot provides a **detailed view of the bill length distribution** within each species. The width of each shape indicates density at different values."
)
fig7 = px.violin(
    df,
    x="species",
    y="bill_length_mm",
    color="species",
    title="Distribution of Bill Length by Species",
    labels={"bill_length_mm": "Bill Length (mm)"},
    box=True,
)
fig7.update_layout(template="plotly_white")
plotly(fig7)

## 8. Bar Chart: Average Body Mass by Sex and Species
text("### Average Body Mass by Sex and Species")
text(
    "This bar chart compares **the average body mass of male and female penguins** for each species, showing how sexual dimorphism affects size."
)
avg_mass = df.groupby(["species", "sex"])["body_mass_g"].mean().reset_index()
fig8 = px.bar(
    avg_mass,
    x="species",
    y="body_mass_g",
    color="sex",
    barmode="group",
    title="Average Body Mass by Sex and Species",
    labels={"body_mass_g": "Average Body Mass (g)", "species": "Species", "sex": "Sex"},
)
fig8.update_layout(template="plotly_white")
plotly(fig8)

## 9. Density Plot of Flipper Length
text("### Density Plot of Flipper Length")
text(
    "This density plot represents the **distribution of flipper lengths** for each species. Unlike a histogram, this provides a smooth approximation of the data."
)
fig9 = ff.create_distplot(
    [
        df[df["species"] == species]["flipper_length_mm"].dropna()
        for species in df["species"].unique()
    ],
    group_labels=df["species"].unique(),
    show_hist=False,
    show_rug=True,
)
fig9.update_layout(title="Density Plot of Flipper Length", template="plotly_white")
plotly(fig9)

## 10. Heatmap of Correlations Between Features
text("### Feature Correlation Heatmap")
text(
    "This heatmap displays the **correlations between numerical features**. Strong positive or negative correlations can indicate relationships between variables."
)
corr_matrix = df[
    ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
].corr()
fig10 = px.imshow(
    corr_matrix,
    text_auto=True,
    color_continuous_scale="viridis",
    title="Feature Correlation Heatmap",
)
plotly(fig10)

# Display the full dataset
text("## Full Dataset")
text("Below is the full dataset used for this analysis.")
table(df)
