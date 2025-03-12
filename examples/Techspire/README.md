# Preswald Project

## Dataset Source Link
https://download.medicaid.gov/data/drp-newly-rprt-drug-03-03-2025-to-03-09-2025.csv

## What does this app do
It shows table and chart listing the drugs reported last week, broken down by day.

## Setup
1. Configure your data connections in `preswald.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py` or just `preswald run`
4. Deploy your app with `preswald deploy --target structured --github [username] --api-key [api-key] hello.py`