# Preswald + MotherDuck Example

This project demonstrates how to connect to MotherDuck from Python using DuckDB.

## Preview

![health](images/HealthDataExample.gif "Health Data Example")

## Quick Start

1. **Install Dependencies**

   ```bash
   pip install duckdb --upgrade
   ```

2. **Set Your MotherDuck Token**  
   Either export it as an environment variable:

   ```bash
   export MOTHERDUCK_TOKEN=<your_motherduck_token>
   ```

   Or include it in the connection string (less secure):

   ```python
   con = duckdb.connect("md:my_db?token=<your_motherduck_token>")
   ```

## Notes

- Make sure you have a valid **MotherDuck** account and token.
- MotherDuck queries work just like DuckDB queries, so you can use all standard SQL commands.
- If you run into issues, check your **MotherDuck** token or review the [MotherDuck Docs](https://www.motherduck.com/) for more details.
