# Netflix Content Analysis Dashboard

## Overview
This interactive dashboard provides comprehensive insights into Netflix's content library, examining growth trends, geographic distribution, genre patterns, and audience targeting. The application is built with Preswald, enabling rapid development of an interactive, data-driven web application without the complexity of traditional full-stack development.

## Dataset
This project uses the Netflix movies and TV shows dataset, which contains detailed information about Netflix content including:
- **Content type** (Movie/TV Show)
- **Title information**
- **Director and cast details**
- **Country of origin**
- **Release date and date added to Netflix**
- **Content rating**
- **Duration**
- **Genre categories**

## Features

### Interactive Elements
- **Sample Display Slider:** Control how many sample rows to display
- **Chart Width Adjustment:** Modify visualization sizes for optimal viewing
- **Year Selection:** Explore content additions by year with an interactive slider

### Multiple Analysis Areas
#### 📊 Dataset Overview
- Dataset structure exploration
- Missing values analysis
- Column cardinality examination

#### 📈 Content Growth Analysis
- Timeline of Netflix content additions
- Movie vs. TV Show growth comparison
- Key business events annotated on timeline

#### 🌎 Geographic Content Distribution
- Top content-producing countries visualization
- Production distribution pie chart
- Interactive choropleth map showing content origins by year

#### 🎭 Genre Analysis
- Genre correlation heatmaps for Movies
- Genre correlation heatmaps for TV Shows
- Cross-format comparison of content strategies

#### 👪 Audience Targeting
- Rating distributions for Movies and TV Shows
- Audience segment analysis across age groups
- Side-by-side format comparison

#### 📅 Content Release Patterns
- Monthly content addition heatmap
- Seasonal pattern analysis
- Year-over-year release strategy comparison

## Data Visualization
- Interactive Plotly charts (line charts, bar charts, pie charts)
- Dynamic choropleth maps
- Correlation heatmaps
- Rating distribution visualizations
- Content addition heatmap
- Responsive design with adjustable visualization sizes

## How to Run

1. **Set Up Your Environment**
   ```bash
   # Install Preswald
   pip install .

   # Create a new project directory
   preswald init netflix_analysis
   cd netflix_analysis
   ```

2. **Configure Data Source**
   Create a `preswald.toml` file in your project directory with the following content:
   ```toml
   [data.netflix]
   path = "./data/netflix_titles.csv"
   ```

3. **Download the Dataset**
   Download the Netflix movies and TV shows dataset and save it as `netflix_titles.csv` in a `data` folder in your project directory.

4. **Run the App Locally**
   ```bash
   preswald deploy
   ```
   This will start a local development server, and you can access the dashboard at the URL shown in the terminal.

## Deployment
Run the following inside the project directory to deploy to Structured Cloud:
```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key>
```
Replace `<your-github-username>` and `<structured-api-key>` with your credentials.

## Implementation Details

### Key Components
- **Data Processing:**
  - Missing value handling
  - Year extraction from date fields
  - Country parsing and normalization
  - Genre extraction and encoding using MultiLabelBinarizer

- **UI Components:**
  - Informative text sections with insights
  - Interactive sliders for visualization control
  - Dynamic tables for data exploration
  - Responsive Plotly visualizations

### Analysis Features
- Content growth timeline with strategic event annotations
- Geographic distribution analysis across countries and time
- Genre correlation analysis with heatmaps
- Content rating distribution by audience segments
- Seasonal content addition pattern detection

## Libraries Used
- **preswald:** Core framework for the application
- **pandas:** Data manipulation and analysis
- **plotly:** Interactive data visualizations
- **numpy:** Numerical operations
- **collections:** Counter for frequency analysis

## Key Insights
- Netflix has strategically shifted from primarily licensing movies to investing heavily in TV shows
- The geographic diversification of content reflects Netflix's international growth strategy
- Different rating distributions between movies and TV shows demonstrate Netflix's approach to audience segmentation
- Genre correlations reveal distinct content strategies for movies versus TV shows
- Content additions follow seasonal patterns aligned with business reporting cycles

## Future Enhancements
- Add support for external libraries to Structured Cloud
- Add markdown list support inside `text` elements

## About This Project
This dashboard demonstrates the power of Preswald for rapidly building and deploying interactive data applications for content strategy analysis.
