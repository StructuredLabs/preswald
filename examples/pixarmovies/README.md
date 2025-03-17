# Pixarmovies Analyzer

The Pixarmovies Project is an analysis tool for Pixar movies built using preswald. It allows users to explore detailed information about each movie, including release dates, box office performance, and critical reception.

## Features
- **Movie Database**: Access detailed information about all Pixar movies.
- **Box Office Analysis**: Analyze box office performance and trends.
- **Critical Reception**: View and compare critical reviews and ratings.

### Prerequisites

1. **Install Python**: Ensure you have Python 3.7 or higher installed. You can download Python from [here](https://www.python.org/downloads/).
   
2. **Install Required Packages**: The project relies on the following Python libraries:
   - `pandas` for data manipulation
   - `plotly` for visualizations
   - `preswald` for app functionality
   - Other dependencies as required for your environment

   To install the required packages, run the following command in your terminal:
   ```bash
   pip install pandas plotly preswald
   ```

## Setup
1. **Configure Data Connections**: 
   - Edit `preswald.toml` to set up your data connections.
2. **Secure Sensitive Information**: 
   - Add your API keys and other sensitive information to `secrets.toml`.
3. **Run Your Application**: 
   - Execute your script using the command: 
     ```bash
     preswald run 
     ```

## Getting Started
To get started with this Project, ensure you have Python installed on your system. Follow the setup steps above to configure your environment and start exploring Pixar movie data.

