Here's a properly formatted `README.md` file that you can **copy and paste** directly into your **VS Code** project:

```markdown
# Preswald Project

## Overview

The **Preswald Project** is a data-driven application for analyzing **Premier Lacrosse League (PLL) performance data (2019-2022)**. It utilizes **Preswald**, a lightweight data visualization framework, to enable dynamic filtering and visualization of key performance metrics such as **win percentage, shooting efficiency, and faceoff percentage**.

## Features

- **Interactive Data Filtering:** Adjust thresholds for shooting efficiency, win percentage, and finishing position.
- **Data Visualization:** Scatter plots to analyze **win percentage vs. shooting efficiency**.
- **Database Integration:** Seamlessly connects to CSV-based datasets.
- **Streamlined UI:** Powered by **Preswald**, built-in UI components allow interactive data exploration.
```

## Project Structure

```
preswald-project/
│── data/ # Dataset storage
│ ├── sample.csv # Source dataset of PLL Statistics
│── images/ # Branding assets
│ ├── logo.png
│ ├── favicon.ico
│── src/
│ ├── hello.py # Main script (entrypoint)
│── .env # Environment variables
│── .gitignore # Ignored files list
│── preswald.toml # Preswald configuration file
│── pyproject.toml # Python project metadata
│── secrets.toml # Secure credentials storage
│── README.md # This file
```

## Installation

### Prerequisites

- Python **3.8+**
- **pip** package manager

### Setup

1. Clone the repository:

   ```sh
   git clone https://github.com/your-repo/preswald-project.git
   cd preswald-project
   ```

2. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Update **secrets.toml** with necessary credentials.
   - Ensure `data/sample.csv` is correctly placed.

## Running the Project

To start the **Preswald server**, run:

```sh
python hello.py
```

This will:

- Start the Preswald UI.
- Load and validate the dataset.
- Render interactive charts and filtering options.

## Configuration

### `preswald.toml`

Defines application metadata:

```toml
[project]
title = "Preswald Project"
port = 8501
entrypoint = "hello.py"

[data.sample_csv]
type = "csv"
path = "data/sample.csv"
```

## Development Guidelines

- Code is formatted using **Black** (`line-length: 88`).
- **isort** is used for import sorting.
- Logging level is set to **CRITICAL** to suppress unnecessary output.
