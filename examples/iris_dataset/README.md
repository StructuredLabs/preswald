# Iris Dataset Analysis and Visualization

## Dataset Source
The dataset used in this project is the **Iris Dataset**, a well-known dataset in the machine learning community. It contains measurements of sepal length, sepal width, petal length, and petal width for three species of the iris flower: *Setosa, Versicolor, and Virginica*.

## Overview of the App
This app provides an interactive analysis of the Iris dataset using **Preswald** and **Plotly** for visualization. It allows users to:

- View summary statistics of the dataset in a tabular format.
- Explore the first few rows of the dataset.
- Filter and view data for a selected iris variety using an interactive slider.
- Visualize data distribution using histograms, scatter matrices, correlation heatmaps, box plots, violin plots, and scatter plots.

## Features
- **Summary Statistics:** Displays key statistical insights about the dataset.
- **Data Filtering:** Allows users to select an iris variety and view relevant data.
- **Visualizations:** Includes various interactive charts like histograms, scatter plots, and box plots.

## How to Run the App
### Prerequisites
Ensure you have the following installed:
- Python 3.x
- `preswald`
- `pandas`
- `plotly`

### Steps to Run
1. Clone this repository:
   ```sh
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```
2. Install dependencies:
   ```sh
   pip install preswald pandas plotly
   ```
3. Run the application:
   ```sh
   preswald run hello.py
   ```

## Deployment
To deploy the app using Preswald, run:
```sh
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```

Replace `<your-github-username>` and `<structured-api-key>` with your actual credentials.

## Notes
- Ensure the **iris.csv** file is available in the `data/` directory.
- The app uses **interactive visualizations** that require a browser-based environment.

## Author
Vishal Basutkar

