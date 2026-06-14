# Frax Balance Sheet

An interactive dashboard built with Preswald to analyze Frax's balance sheet data. Features include dynamic filtering, SQL queries, and beautiful visualizations.

## Features
- Interactive asset analysis with dynamic filtering
- SQL-based querying for data exploration
- Data visualization with scatter plots and pie charts
- CSV-based data management for easy updates

## Running with Docker
1. Build the Docker image:
   ```bash
   docker build -t frax-balance-sheet .
   ```

2. Run the container:
   ```bash
   docker run -p 8501:8501 frax-balance-sheet
   ```

3. Open the app in your browser:
   ```
   http://localhost:8501
   ```

## Project Structure
- `hello.py`: Main application code with Preswald components
- `preswald.toml`: Configuration for data sources and app settings
- `data/frax_assets.csv`: Asset data in CSV format
- `Dockerfile`: Docker configuration for containerized deployment

## Development
This app is built using the Preswald framework, which provides powerful tools for building interactive data apps. The app runs in a Docker container for consistent development and deployment.