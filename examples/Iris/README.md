# Iris Data Analysis App

This project is a simple data analysis application built using **Preswald** and **Plotly**. It loads the famous **Iris dataset**, applies filtering using SQL queries and sliders, and visualizes the data through interactive tables and scatter plots.

## Dataset Source
The **Iris dataset** is a well-known dataset in machine learning and statistics. It contains measurements of 150 iris flowers from three species (*Setosa, Versicolor, and Virginica*), including sepal length, sepal width, petal length, and petal width. The dataset is commonly used for classification and pattern recognition tasks.

## Features

- **Load Data**: Retrieves the Iris dataset using `get_df("Iris")`.
- **SQL Query Filtering**: Filters the dataset where `PetalLengthCm > 1.5`.
- **Dynamic Data Filtering**: Users can adjust the petal length threshold with a slider.
- **Data Visualization**: Displays a scatter plot of Sepal Length vs. Sepal Width, color-coded by species.

## Technologies Used

- [Preswald](https://preswald.io/) for data processing and interactive UI components.
- [Plotly](https://plotly.com/python/) for data visualization.
- Python for scripting and application logic.

## Code Overview

```python
from preswald import connect, get_df, query, table, text, slider, plotly
import plotly.express as px

connect()
df = get_df("Iris")

print("Dataset Columns:", df.columns)

# SQL Query to filter data
sql = "SELECT * FROM Iris WHERE PetalLengthCm > 1.5"
filtered_df = query(sql, "Iris")

# UI Components
text("# Iris Data Analysis App")
table(filtered_df, title="Filtered Iris Data (Petal Length > 1.5)")

threshold = slider("Minimum Petal Length", min_val=0.5, max_val=6.5, default=1.5)
table(df[df["PetalLengthCm"] > threshold], title="Dynamic Iris Data View")

# Scatter plot visualization
fig = px.scatter(df, x="SepalLengthCm", y="SepalWidthCm", color="Species")
plotly(fig)
```

## Usage
- Run the script to launch the analysis dashboard.
- Use the slider to filter the dataset interactively.
- View the scatter plot for visual insights.

## Deployment
To deploy the app using Preswald, run:
```bash
preswald deploy
```

## License
This project is licensed under the MIT License.

