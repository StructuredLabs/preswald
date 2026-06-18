# Global Temperature Analysis

An interactive dashboard application built with Preswald for visualizing and analyzing historical global temperature trends using temperature anomaly data (1880-2023).

## Overview

This application provides interactive visualizations of global temperature anomalies, allowing users to:
- Explore temperature changes over different time scales
- Analyze seasonal patterns and trends
- Examine statistical summaries and uncertainty metrics
- Filter data by custom year ranges

## Dataset Information

This project uses the `GlobalTemperatures.csv` dataset containing historical temperature anomaly measurements:

- **Temperature Anomaly**: Deviation from a baseline temperature (typically a 30-year average)
- **Time Scales**: Monthly, Annual, 5-Year, 10-Year, and 20-Year measurements
- **Uncertainty Values**: Statistical uncertainty measurements for each anomaly value
- **Date Range**: Multi-decade historical temperature record (1880-2023)

## Features

- **Interactive Controls**
  - Date range selection with sliders
  - Custom smoothing parameter adjustment
  
- **Multiple Visualizations**
  - Time series comparison of different anomaly scales
  - Trend analysis with statistical regression
  - Seasonal patterns (monthly averages and heatmaps)
  - Uncertainty range visualization
  
- **Statistical Analysis**
  - Key metrics (averages, extremes, trends)
  - Decade-wise summary statistics
  - Rate of change calculations

## Getting Started

### Prerequisites
- Python 3.7+
- Preswald framework

### Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml` (not included in version control)

### Running Locally

```bash
preswald run
```

## Deployment

Deploy to Structured Cloud with:

```bash
preswald deploy --target structured --github <your-github-username> --api-key <your-api-key>
```