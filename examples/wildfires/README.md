# Preswald Coding Assesment
This is an application that display data about California Wildfires in a meaningful way using the Preswald framework, data is pulled from [Kaggle](https://www.kaggle.com/datasets/vivekattri/california-wildfire-damage-2014-feb2025)

## Prerequisties
  You must have Python 3 installed on your local enviroment

## Features
  * Displays data on a bar chart (eg. Location vs the column user filters by)
  * User can filter data by column (eg. Houses, Businesses Destroyed, or Financial loss)
  * User can filter data by year or display all records
  * Each incident is categorized by the "Cause" column

## Installation

Follow the steps to run the project locally

Navigate to the `examples/wildfires` directory

```bash
# current dir /
cd examples/wildfires

```

Setup a virtual environment

```bash
# wildfires
python3 -m venv env
source env/bin/activate

```

install preswald dependency & run locally

```bash
# wildfires
pip install preswald
preswald run

```

## Deployment
Create account on preswald create an API key and run 
```bash
preswald deploy --target structured --github <your-github-username> --api-key <structured-api-key> hello.py
```






