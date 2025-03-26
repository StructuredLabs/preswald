# Ireland Gender Pay Gap Analysis

App is available at: https://pay-gap-project-545637-a08wcfqn-ndjz2ws6la-ue.a.run.app/

This application uses [Preswald](https://github.com/presw-ald/preswald) to produce interactive visualizations and tables for exploring Ireland’s Gender Pay Gap data.

## Table of Contents

1. [Overview](#overview)
2. [Installation & Environment Setup](#installation--environment-setup)
3. [Running the Application](#running-the-application)
4. [Data Description](#data-description)

---

## Overview

This project demonstrates how to filter, visualize, and interact with real-world pay gap data. The code:

1. Performs a SQL-like query on the “irish_pay_gap” dataset (selecting rows where `Report Year > 2022`).
2. Displays data in a table with a configurable slider (so that users can filter out rows based on the "Median Hourly Gap").
3. Creates (for the top 20 companies based on the number of not null columns):
   - A grouped bar chart comparing Mean/Median Hourly and Bonus Gaps.
   - A scatter (bubble) chart showing relationships between Mean Hourly Gap, Mean Bonus Gap, and the percentage of female employees at each company.

---

## Installation & Environment Setup

1. **Clone or Download** this repository.
2. **Create a Python virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On macOS / Linux
   # or
   .\venv\Scripts\activate    # On Windows
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Application

1. Once your environment is active and dependencies installed, run:
   ```bash
   preswald run
   ```
2. Preswald will launch a local server. Open the provided URL in your web browser to see the application and interact with the charts and tables.

---

## Data Description

A snapshot of the CSV data being used for this analysis (named `irish_pay_gap`) has the following columns:

- **Sr. Number**
- **Company Name**
- **Report Year**
- **Mean Hourly Gap**
- **Median Hourly Gap**
- **Mean Bonus Gap**
- **Median Bonus Gap**
- **Mean Hourly Gap Part Time**
- **Median Hourly Gap Part Time**
- **Mean Hourly Gap Part Temp**
- **Median Hourly Gap Part Temp**
- **Percentage Bonus Paid Female**
- **Percentage Bonus Paid Male**
- **Percentage BIK Paid Female**
- **Percentage BIK Paid Male**
- **Q1 Female, Q1 Male, Q2 Female, Q2 Male, …, Q4 Male**
- **Percentage Employees Female**
- **Percentage Employees Male**

Not all records have every field populated, so the code sorts by the number of non-null columns and takes the top 20 companies with highest number of not null values to ensure you see the most complete data.
