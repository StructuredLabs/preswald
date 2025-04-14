Olympics Medal Analysis

Overview

This project provides an interactive dashboard for analyzing Olympics medal data from 1896 to 2024. Users can filter data based on year, country, and minimum medal count. The dashboard presents tabular results along with visualizations using bar and scatter plots.

Features

Filter by Year: Search for Olympic data by entering a specific year or part of a year.

Filter by Country: Search by country code (e.g., "USA"). Partial matches are supported.

Filter by Minimum Medals: Show only countries with a specified minimum total medal count.

Visualizations:

Bar chart for medal distribution (Gold, Silver, Bronze)

Scatter plot for total medals over the years

Scatter plot comparing Gold medals vs. total medals

Dependencies

Ensure you have the following dependencies installed:

preswald

pandas

plotly

Installation

pip install preswald pandas plotly

Usage

Connect to Data: The script connects to an Olympics dataset (olympics_csv).

Input Fields:

Enter a year (optional, supports partial input)

Enter a country code (optional, supports partial input)

Enter minimum medals (optional, defaults to 0 if left blank)

Filtering & Query Execution: A SQL query is built dynamically based on inputs.

Results & Visualizations:

If filtered data exists, it is displayed in a table.

Bar and scatter plots visualize medal distribution and trends.

SQL Query Structure

The filtering logic dynamically builds a SQL query:

SELECT * FROM olympics_csv
WHERE 1=1
AND CAST(Year AS TEXT) LIKE '%<selected_year>%'
AND NOC LIKE '%<selected_country>%'
AND (Gold + Silver + Bronze) >= <min_medals>

Example Scenario

User Inputs:

Year: 2020

Country Code: USA

Minimum Medals: 10

Generated SQL Query:

SELECT * FROM olympics_csv
WHERE 1=1
AND CAST(Year AS TEXT) LIKE '%2020%'
AND NOC LIKE '%USA%'
AND (Gold + Silver + Bronze) >= 10

Output:

A table listing all relevant Olympic events meeting the criteria.

A bar chart showing the count of Gold, Silver, and Bronze medals.

A scatter plot illustrating total medals won by USA over the years.

A scatter plot comparing Gold medals with total medals.