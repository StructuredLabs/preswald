# JPMorgan Chase Stock Data Visualization (1980 - 2025)

## Overview
This Preswald application provides an interactive visualization of JPMorgan Chase & Co.'s stock data from 1980 to 2025. It includes market capitalization, revenue, and earnings trends, leveraging `pandas` for data manipulation and `plotly.express` for visualizations.

## Dataset
- **Source**: The dataset used in this project is `JPM_1940-01-01_2025-03-04.csv` present in the `data` folder, which contains historical stock data for JPMorgan Chase. It was originally shared on [kaggle](https://www.kaggle.com/datasets/umerhaddii/jpmorgan-chase-stock-data-2025/data) by Umer Haddii.
- **Columns**: The dataset includes columns such as `date`, `open`, `high`, `low`, `close`, `volume`, and other stock market indicators.
- **Preprocessing**: The `date` column is converted to `datetime` for proper formatting and visualization.

## Features of the Application
1. **Market Capitalization Analysis**  
   - Market cap is calculated as `closing price × outstanding shares (2.8 billion)`.  
   - An interactive area chart visualizes the trend of market capitalization over time.  
   - A dynamic annotation is added to highlight the latest market cap value.

2. **Revenue Analysis**  
   - Revenue is estimated as `volume × closing price`.  
   - An area chart represents the revenue trend, with interactive hover features.  
   - The latest revenue value is annotated for easy reference.

3. **Earnings Analysis**  
   - Earnings per share (EPS) is calculated as `revenue ÷ outstanding shares`.  
   - A dedicated earnings visualization tracks the changes in EPS over time.  
   - Annotation highlights the latest earnings value.

## How to Run the Application
### Prerequisites
Ensure you have `preswald`, `pandas`, and `plotly` installed. If not, install them using:
```bash
pip install preswald pandas plotly
```

### Running the Application
1. Clone [this repository](https://github.com/devilkiller-ag/JP-Morgan-Chase-Stock-Visualization) and navigate to the project folder:
   ```bash
   git clone https://github.com/devilkiller-ag/JP-Morgan-Chase-Stock-Visualization.git
   cd JP-Morgan-Chase-Stock-Visualization
   ```
2. Download the dataset from [this link](https://www.kaggle.com/datasets/umerhaddii/jpmorgan-chase-stock-data-2025/data) and place it in the `data` folder.

3. Run the script using Preswald:
   ```bash
   preswald run
   ```
4. Open the application in your browser to interact with the visualizations.

## About the Author
- **Name**: Ashmit JaiSarita Gupta
- **Portfolio**: [Ashmit's Website](https://www.ashmit.dev)
- **LinkedIn**: [Ashmit's LinkedIn Profile](https://www.linkedin.com/in/ashmit-jaisarita-gupta/)
- **GitHub**: [Ashmit's GitHub Profile](https://github.com/devilkiller-ag/)
- **Twitter**: [Ashmit's Twitter Profile](https://x.com/jaisarita)  
