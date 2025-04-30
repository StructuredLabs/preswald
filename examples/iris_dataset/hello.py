from preswald import text, plotly, connect, table, slider
import pandas as pd
import plotly.express as px

# Welcome message
text("## Unveiling the Secrets of Iris: Data Analysis and Classification. 🌸")

# Load the CSV
connect()  # Load in all sources, default is the sample_csv
df = pd.read_csv('data/iris.csv')

# Show summary statistics in a table format
text("### Summary Statistics")
summary_df = df.describe().reset_index().rename(columns={"index": "Statistic"})
table(summary_df)

# Show first few rows of the data
text("### First 5 Rows of Data")
table(df.head())

# Add an interactive slider for selecting variety
variety_options = df["variety"].unique()
slider_value = slider("Select Iris Variety", min_val=0, max_val=len(variety_options) - 1, default=0)
selected_variety = variety_options[slider_value]

# Filter the dataframe based on the selected variety
filtered_df = df[df['variety'] == selected_variety]

# Display the filtered table
table(filtered_df, title=f"Data for {selected_variety}")

# Distribution of classes (species)
text("### Distribution of Iris Species")
fig1 = px.histogram(df, x='variety', title="Distribution of Iris Species", color="variety")
plotly(fig1)

# Scatter Matrix for relationships between features
text("### Scatter Matrix of Features")
fig2 = px.scatter_matrix(df, dimensions=df.columns[:-1], color='variety', title="Scatter Matrix of Iris Features")
plotly(fig2)

# Correlation heatmap between features
text("### Correlation Heatmap")
correlation_matrix = df.corr(numeric_only=True)  # Ensure only numeric columns are used
fig3 = px.imshow(correlation_matrix, text_auto=True, color_continuous_scale='RdBu', title="Correlation Heatmap")
plotly(fig3)

# Box Plot for visualizing feature distribution
text("### Box Plot of Iris Features")
fig4 = px.box(df, x="variety", y="sepal.length", color="variety", title="Sepal Length Distribution by Variety")
plotly(fig4)

# Violin Plot for feature density visualization
text("### Violin Plot for Feature Density")
fig5 = px.violin(df, x="variety", y="petal.width", box=True, points="all", color="variety", title="Petal Width Distribution by Variety")
plotly(fig5)

# Scatter Plot for Sepal vs Petal measurements
text("### Sepal vs Petal Comparison")
fig6 = px.scatter(df, x="sepal.length", y="petal.length", color="variety", size="sepal.width", hover_data=["petal.width"], 
                  title="Sepal Length vs Petal Length")
plotly(fig6)
