# Startup Failures Visualization

## Overview
This **Preswald** app visualizes startup failures, allowing users to explore startups that ceased operations over time. It provides an interactive scatter plot and a dynamic table filtered by **start year** and **end year**.

## Dataset
The dataset consists of failed startups, including their industry sector, years active, and start/end dates.

Example rows:
```csv
name,sector,years,start,end
99dresses,Retail Trade,3,2010,2013
Ahalife,Retail Trade,7,2010,2017
Airy Labs,Information,2,2010,2012
AllRomance,Retail Trade,10,2006,2016
```

The full dataset is included in `data/startup_failures.csv`.

## Features
- **Scatter plot** visualizing the **start** and **end** years of failed startups.
- **SQL query filtering** for startups that began after 2015.
- **Interactive slider** to adjust the end year threshold dynamically.
- **Table display** showing filtered startup data.

## How to Run
Ensure you have **Preswald** installed and navigate to the project directory:
```bash
preswald run
```

## How to Deploy
Deploy the app using the following command:
```bash
preswald deploy --target structured --github <my-github-name> --api-key <my-api-key>
```
