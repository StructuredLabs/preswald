# Iris Dataset Explorer

This example demonstrates an interactive data explorer built with **Preswald** using the classic **Iris dataset**. The app loads the dataset, displays key statistics, and provides interactive visualizations to analyze petal and sepal dimensions by species.

## Features

- **Automatic Data Loading:**  
  The app attempts to load the Iris dataset using common names and file paths. If the dataset is not found, it generates sample data for demonstration.
  
- **Dataset Overview:**  
  Displays the number of samples, features, a preview of the first few rows, and basic statistical summaries.

- **Interactive Visualizations:**  
  Provides scatter plots for:
  - **Sepal Dimensions:** Visualizing sepal length versus sepal width.
  - **Petal Dimensions:** Visualizing petal length versus petal width.
  
- **Filtering:**  
  Includes an interactive slider to dynamically filter the dataset based on sepal length.

## Prerequisites

- Python 3.8 or higher.
- [Preswald](https://github.com/StructuredLabs/preswald) installed.  
  You can install it via pip:
  ```bash
  pip install preswald
  ```

## How to Run

If you have updated your PATH environment variable, you can simply run:

```bash
preswald run hello.py
```

**For Windows users without the Preswald CLI in your PATH:**  
Use the full path to the executable. For example:
```bash
C:\Users\user\AppData\Roaming\Python\Python313\Scripts\preswald.exe run hello.py
```
Make sure to adjust the path if your Python installation differs.

## File Structure

```
iris_example/
├── hello.py         # Main application script
├── data/
│   └── iris.csv     # Iris dataset CSV (if available; otherwise, sample data is used)
└── README.md        # This file
```

## How It Works

- The application starts by connecting to its data sources.
- It attempts to load the Iris dataset using several common names.
- If the dataset isn’t found, it looks for the file in various paths or creates sample data.
- The app then displays:
  - An overview of the dataset.
  - A preview of the first five rows.
  - Statistical summaries of numeric features.
- Interactive scatter plots visualize the relationships between sepal and petal dimensions.
- A slider allows users to filter data based on sepal length dynamically.
