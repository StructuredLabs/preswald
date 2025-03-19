# Global Renewable Energy Adoption Analysis

## Overview
This interactive visualization application analyzes renewable energy adoption trends across major countries from 1965 to 2021. The application provides multiple visualizations and statistical analyses to help understand the progression of renewable energy adoption globally.

## Dataset
**Source**: [https://www.kaggle.com/datasets/belayethossainds/renewable-energy-world-wide-19652022]

The dataset contains annual renewable energy adoption percentages for various countries and regions, including:
- Time period: 1965-2021
- Metrics: Renewable energy share as a percentage of total energy consumption
- Geographic coverage: Multiple countries and regions including:
  - United States
  - China
  - Germany
  - United Kingdom
  - World average

## Features
The application includes several interactive visualizations:

1. **Historical Trend Line Plot**
   - Shows continuous progression from 1965-2021
   - Color-coded by country
   - Interactive hover details
   - Highlights key transition periods

2. **Five-Year Average Bar Chart**
   - Displays adoption rates in 5-year intervals
   - Facilitates period-over-period comparison
   - Groups countries for easy comparison

3. **Distribution Scatter Plot**
   - Point sizes indicate magnitude of renewable share
   - Focuses on post-2000 adoption patterns
   - Reveals clustering and outlier patterns

4. **Statistical Summary Table**
   - Recent period analysis (2015-2021)
   - Shows mean, minimum, and maximum adoption rates
   - Provides quick comparative metrics

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)

### Setup Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/aadamgough/preswald
   cd preswald/community_gallery
   ```

2. Install required packages:
   ```bash
   pip install preswald pandas plotly
   ```

3. Verify the installation:
   ```bash
   python3 --version
   pip list
   ```

## Running the Application

### Local Development
1. Navigate to the project directory:
   ```bash
   cd renewable_energy_oa
   ```

2. Run the application:
   ```bash
   preswald run
   ```

### Deployment
1. Ensure you have a Preswald API key
Visit Preswald Platform.
Create a new organization by selecting "Create New Organization" in the top left corner.
Navigate to Settings > API Keys.
Click on "Generate" to create a new API key and copy it.

2. Deploy using the Preswald CLI:
   ```bash
   preswald deploy --target structured --github [your-github-username] --api-key [your-api-key] hello.py
   ```

3. Access your deployed application at the URL provided by Preswald

Following these steps will host your application on Structured Cloud, making it accessible online. Verify your deployment to ensure all functionalities work correctly.
