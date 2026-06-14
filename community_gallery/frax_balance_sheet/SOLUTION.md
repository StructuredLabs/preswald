# Preswald Coding Assessment Solution

## Overview
I have created an interactive Frax balance sheet analysis application using the Preswald framework. The app provides dynamic data visualization and analysis tools for exploring Frax's asset distribution.

## Features Implemented
1. **Data Loading and Management**
   - CSV-based data source configuration in `preswald.toml`
   - Asset data stored in `data/frax_assets.csv`

2. **Interactive Analysis**
   - SQL queries for filtering major assets
   - Dynamic threshold filtering with sliders
   - Real-time updates of filtered data

3. **Visualizations**
   - Scatter plot showing asset distribution
   - Pie chart displaying asset composition
   - Interactive data tables

4. **Deployment**
   - Docker containerization for consistent deployment
   - Local deployment working successfully
   - All features functional in containerized environment

## Technical Implementation
- Used Preswald's native components (text, table, slider, plotly)
- Implemented SQL-based data querying
- Added interactive controls for dynamic filtering
- Created responsive visualizations with Plotly

## Running the App
1. Clone the repository:
   ```bash
   git clone https://github.com/erosnol/preswald-frax.git
   cd preswald-frax
   ```

2. Run with Docker:
   ```bash
   docker build -t frax-balance-sheet .
   docker run -p 8501:8501 frax-balance-sheet
   ```

3. Open in browser:
   ```
   http://localhost:8501
   ```

## Repository Structure
```
preswald-frax/
├── hello.py           # Main application code
├── preswald.toml      # Configuration file
├── data/
│   └── frax_assets.csv # Asset data
├── Dockerfile         # Docker configuration
└── README.md         # Project documentation
```

## Notes
- Successfully implemented all required features from the assessment
- Added extra functionality for better user experience
- Ensured code quality and documentation
- Provided Docker deployment for easy testing
