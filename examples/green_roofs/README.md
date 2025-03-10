# Green Roofs in San Francisco - Data Visualization
## Preview
[Live Preview Link - Click Me](https://preswald-my-example-project-167719-wfeaikvx-ndjz2ws6la-ue.a.run.app/)

## Overview
This project provides interactive visualizations of **green roofs** in San Francisco using `Plotly`, `GeoPandas`, and `Preswald`. The dataset includes information about green roof locations, building types, installation years, costs, and other attributes. The visualizations aim to help users explore trends, distribution, and insights about green roofs in the city.

## Features
- **Interactive Map:** Displays green roof locations using `Scattermapbox`.
- **Cost vs. Size Analysis:** Compares the cost of green roofs to their size while ensuring proper scaling.
- **Yearly Installation Trends:** Visualizes the number of green roofs installed each year, excluding invalid values.
- **Building Use Distribution:** Shows the count of green roofs by building type (`Building_U`), sorted by frequency.
- **Built vs. Unfinished Buildings:** Differentiates between completed and unfinished green roofs based on installation year.

## Installation & Setup
### Prerequisites
Ensure you have Python installed along with the following libraries:
```sh
pip install pandas geopandas plotly preswald
```

### Running the App
1. Clone the repository (if applicable):
   ```sh
   git clone <repository-url>
   cd green-roofs-visualization
   ```
2. Launch the Preswald environment:
   ```sh
   preswald hello.py
   ```
3. Open the interactive visualization in your browser.

## Data Processing
- **CRS (Coordinate Reference System):** The dataset's spatial information is converted to `EPSG:4326` (WGS84) for compatibility with `Plotly`.
- **Filtering:** Green roofs with `YearBuilt = 0` are excluded to improve accuracy in time-based analyses.
- **Categorization:** Buildings are labeled as "Built" or "Unfinished" based on their installation year.
- **Sorting:** `Building_U` values are sorted by frequency to enhance readability.

## Visualizations
### 1. Interactive Map
**Description:** A map displaying all green roof locations with building names and addresses.
- **Latitude/Longitude** extracted from `the_geom` column.
- Uses `Scattermapbox` for plotting.

### 2. Yearly Installation Trends
**Description:** A line chart showing the number of green roofs installed each year.
- **Filtering:** Excludes buildings with missing or zero installation years.
- **Rescaled X-axis:** Ensures the earliest installation year appears on the leftmost side.

### 3. Building Use Distribution
**Description:** A bar chart displaying green roofs categorized by `Building_U`, sorted by frequency.
- **Stacked bars:** Different building types are color-coded.
- **Sorted by Count:** Helps highlight the most common building types with green roofs.