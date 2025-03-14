# Iris Dataset Example

## Dataset Source
The Iris dataset is a classic dataset in machine learning, originally collected by Edgar Anderson and popularized by Ronald Fisher. It contains measurements of iris flowers from three different species: setosa, versicolor, and virginica.

Source: [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/iris)

## App Description
This Preswald app allows users to interactively explore the Iris dataset. It features:
- A slider to filter the data based on the minimum petal length.
- A table displaying the filtered data.
- A scatter plot of sepal length vs. sepal width, colored by species, updating based on the filter.

## How to Run
1. Ensure you have Preswald installed: `pip install preswald`
2. Navigate to the project directory: `cd community_gallery/iris_example`
3. Run the app locally: `preswald run hello.py`
4. Open the provided local server link in your browser.

## How to Deploy
1. Obtain an API key from [app.preswald.com](https://app.preswald.com/).
2. Deploy using: `preswald deploy --target structured --github <your-github-username> --api-key <your-api-key> hello.py`
3. Access the live app via the provided link.