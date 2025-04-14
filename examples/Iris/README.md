# Iris Data Analysis App

This project is a data visualization and analysis application for the **Iris dataset**, utilizing **Preswald** and **Plotly** to create interactive tables and visualizations.

## Dataset Source
The **Iris dataset** is a well-known dataset in machine learning and statistics. It contains measurements of 150 iris flowers from three species (*Setosa, Versicolor, and Virginica*), including sepal length, sepal width, petal length, and petal width.

## Features

- **Load Data**: Retrieves the Iris dataset using `get_df("Iris")`.
- **SQL Query Filtering**: Filters the dataset where `PetalLengthCm > 1.5`.
- **Dynamic Data Filtering**: Users can adjust the petal length threshold with a slider.
- **Data Visualization**:
  - Scatter plot of Sepal Length vs. Sepal Width, color-coded by species.
  - Histogram of Petal Length distribution.
  - Box plot comparing Sepal Width across species.
  - Pie chart showing the proportion of each species in the dataset.
  - Correlation heatmap to analyze feature relationships.
- **UI Enhancements**:
  - Interactive slider for filtering.
  - Searchable and dynamic data tables.

## Technologies Used
- **Preswald** for data processing and interactive UI components.
- **Plotly** for data visualization.
- **Python** for scripting and application logic.

## Code Explanation
The script follows these steps:

1. **Connect to Data Source**
   ```python
   connect()
   df = get_df("Iris")
   ```
   - Establishes a connection using `connect()` and retrieves the Iris dataset using `get_df("Iris")`.

2. **SQL Query Filtering**
   ```python
   sql = "SELECT * FROM Iris WHERE PetalLengthCm > 1.5"
   filtered_df = query(sql, "Iris")
   ```
   - Uses an SQL query to filter rows where `PetalLengthCm > 1.5`.

3. **UI Components and Data Display**
   ```python
   text("# Iris Data Analysis App")
   table(filtered_df, title="Filtered Iris Data (Petal Length > 1.5)")
   ```
   - Displays the title and filtered data table in the UI.

4. **Slider for Dynamic Filtering**
   ```python
   threshold = slider("Minimum Petal Length", min_val=0.5, max_val=6.5, default=1.5)
   table(df[df["PetalLengthCm"] > threshold], title="Dynamic Iris Data View")
   ```
   - Allows users to filter data dynamically based on the chosen `PetalLengthCm` threshold.

5. **Scatter Plot for Sepal Length vs Sepal Width**
   ```python
   fig_scatter = px.scatter(df, x="SepalLengthCm", y="SepalWidthCm", color="Species")
   plotly(fig_scatter)
   ```
   - Creates and displays a scatter plot visualizing Sepal Length vs. Sepal Width.

6. **Additional Visualizations**
   - **Histogram**: Visualizes the distribution of Petal Lengths.
   - **Box Plot**: Compares Sepal Width across species.
   - **Pie Chart**: Shows the species distribution.
   - **Correlation Heatmap**: Displays the relationships between numerical features.

## Installation & Setup

1. Install the required dependencies:
   ```bash
   pip install preswald plotly pandas
   ```

2. Run the application:
   ```python
   python app.py
   ```

## Usage
- Run the script to launch the analysis dashboard.
- Use the slider to filter the dataset interactively.
- View various visualizations to understand data distribution and relationships.

## Deployment
To deploy the app using Preswald, run:
```bash
preswald deploy
```

## License
This project is licensed under the MIT License.

