# Preswald Airbnb Market Intelligence Dashboard

## Overview
This interactive dashboard provides comprehensive insights into San Francisco's Airbnb market, helping users understand pricing trends, neighborhood dynamics, and host behaviors. The application is built with Preswald, enabling rapid development of an interactive, data-driven web application without the complexity of traditional full-stack development.

## Dataset
This project uses the San Francisco Airbnb dataset, which contains detailed information about Airbnb listings in San Francisco, including:
- **Listing details** (price, property type, minimum nights)
- **Location information** (neighborhood)
- **Host information** (host ID, host name)
- **Review metrics** (reviews per month, last review date)
- **Availability information**

**Source:** The dataset is from Inside Airbnb ([http://insideairbnb.com/get-the-data/](http://insideairbnb.com/get-the-data/)), which provides publicly available data scraped from Airbnb's website.

## Features

### Interactive Filters
- **Neighborhood Selection:** Filter listings by specific neighborhoods or view all
- **Property Type Filter:** Filter by room type (Entire home/apt, Private room, Shared room)
- **Apply Filters Button:** Dynamic filtering with real-time feedback on result count

### Multiple Dashboard Views
#### 📊 Market Overview
- Key market indicators (average price, median price, etc.)
- Property type distribution with pie chart
- Price distribution histogram with statistics
- Top neighborhoods by listing count

#### 🗺️ Neighborhood Analysis
- Average price by neighborhood with bar charts
- Room type distribution by neighborhood
- Price heatmap showing average prices by neighborhood and room type

#### 💰 Price Insights
- Price distribution by property type with box plots
- Price vs. minimum stay analysis
- Price vs. review frequency scatter plots
- Detailed price statistics by property type

#### 👥 Host Analysis
- Host listing count distribution
- Top hosts by number of listings
- Average price analysis by host portfolio size

#### ⭐ Reviews & Ratings
- Reviews per month distribution
- Average reviews by property type
- Review recency analysis

## Data Visualization
- Interactive Plotly charts (pie charts, bar charts, scatter plots, histograms)
- Color-coded heatmaps
- Responsive design that adjusts to filtering
- Insights highlighting key findings from each visualization

## How to Run

1. **Set Up Your Environment**
   ```bash
   # Install Preswald and other libraries
   pip install preswald pandas numpy matplotlib plotly scikit-learn

   # Create a new project directory
   preswald init airbnb_dashboard
   cd airbnb_dashboard
   ```

2. **Configure Data Source**
   Create a `preswald.toml` file in your project directory with the following content:
   ```toml
   [data.airbnb]
   path = "./data/airbnb.csv"
   ```

3. **Download the Dataset**
   Download the San Francisco Airbnb dataset from Inside Airbnb and save it as `airbnb.csv` in a `data` folder in your project directory.

4. **Run the App Locally**
   ```bash
   preswald run hello.py
   ```
   This will start a local development server, and you can access the dashboard at the URL shown in the terminal.

## Deployment
Deploy to Structured Cloud:
```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```
Replace `<your-github-username>` and `<structured-api-key>` with your credentials.

## Implementation Details

### Key Components
- **Data Processing:**
  - Datetime conversion for review dates
  - Price categorization with bins
  - Days since review calculations
  - Interactive filtering logic

- **UI Components:**
  - Text displays for insights
  - Interactive selectboxes for navigation and filtering
  - Interactive table for data display
  - Responsive Plotly visualizations

### Analysis Features
- Statistical summaries (averages, medians, counts)
- Distribution analysis
- Comparative analysis between neighborhoods and property types
- Host portfolio analysis
- Time-based review analysis

## Libraries Used
- **preswald:** Core framework for the application
- **pandas:** Data manipulation and analysis
- **plotly:** Interactive data visualizations
- **numpy:** Numerical operations
- **datetime:** Date and time handling

## Future Enhancements
- Add map-based visualizations for geographic insights
- Implement predictive pricing models based on property attributes
- Add seasonality analysis of pricing and availability
- Include sentiment analysis from review text data

## About This Project
This dashboard was created as part of the Structured Labs coding assessment. It demonstrates the power of Preswald for rapidly building and deploying interactive data applications.