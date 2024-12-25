import os
import click
from preswald.server import start_server


@click.group()
def cli():
    """
    Preswald CLI - A lightweight framework for interactive data apps.
    """
    pass


@cli.command()
@click.argument("name", default="preswald_project")
def init(name):
    """
    Initialize a new Preswald project.

    This creates a directory with boilerplate files like `hello.py` and `config.toml`.
    """
    try:
        os.makedirs(name, exist_ok=True)

        # Create boilerplate files
        with open(os.path.join(name, "hello.py"), "w") as f:
            f.write(
                '''from preswald import text, connect, view

# Connect to data sources
# You can use the config.toml file to configure your connections
# or connect directly using the source parameter:

# Example connections:
# db = connect(source="postgresql://user:pass@localhost:5432/dbname")
# csv_data = connect(source="data/file.csv")
# json_data = connect(source="https://api.example.com/data.json")

# Or use the configuration from config.toml:
# db = connect()  # Uses the default_source from config.toml

text("# Welcome to Preswald!")
text("This is your first app. 🎉")

# Example: View data from a connection
# view("connection_name", limit=50)
'''
            )

        with open(os.path.join(name, "config.toml"), "w") as f:
            f.write(
                '''[project]
title = "Preswald Project"
version = "0.1.0"
port = 8501

[theme.color]
primary = "#4CAF50"
secondary = "#FFC107"
background = "#FFFFFF"
text = "#000000"

[theme.font]
family = "Arial, sans-serif"
size = "16px"

[data]
default_source = "postgres"   # Default data source. Options: "csv", "postgres", "mysql", "json", "parquet"
cache = true                  # Enable caching of data

[data.postgres]
host = "localhost"            # PostgreSQL host
port = 5432                   # PostgreSQL port
dbname = "mydb"              # Database name
user = "user"                # Username
# password is stored in secrets.toml

[data.mysql]
host = "localhost"           # MySQL host
port = 3306                 # MySQL port
dbname = "mydb"            # Database name
user = "user"              # Username
# password is stored in secrets.toml

[data.csv]
path = "data/sales.csv"    # Path to CSV file

[data.json]
url = "https://api.example.com/data"  # URL for JSON data
# api_key is stored in secrets.toml

[data.parquet]
path = "data/sales.parquet"  # Path to Parquet file
'''
            )

        with open(os.path.join(name, "secrets.toml"), "w") as f:
            f.write('''# Add your secrets here (DO NOT commit this file)

[data.postgres]
password = ""  # PostgreSQL password

[data.mysql]
password = ""  # MySQL password

[data.json]
api_key = ""  # API key for JSON endpoint
'''
            )

        with open(os.path.join(name, ".gitignore"), "w") as f:
            f.write("secrets.toml\n")

        with open(os.path.join(name, "README.md"), "w") as f:
            f.write('''# Preswald Project

## Setup
1. Configure your data connections in `config.toml`
2. Add sensitive information (passwords, API keys) to `secrets.toml`
3. Run your app with `preswald run hello.py`
'''
            )

        click.echo(f"Initialized a new Preswald project in '{name}/'")
    except Exception as e:
        click.echo(f"Error initializing project: {e}")


@cli.command()
@click.argument("script", default="hello.py")
@click.option("--port", default=8501, help="Port to run the server on.")
def run(script, port):
    """
    Run a Preswald app.

    By default, it runs the `hello.py` script on localhost:8501.
    """
    if not os.path.exists(script):
        click.echo(f"Error: Script '{script}' not found.")
        return

    click.echo(f"Running '{script}' on http://localhost:{port}")
    start_server(script=script, port=port)


@cli.command()
@click.option("--port", default=8501, help="Port for local deployment.")
def deploy(port):
    """
    Deploy your Preswald app locally.

    This allows you to share the app within your local network.
    """
    try:
        click.echo(f"Deploying app locally on http://localhost:{port}...")
        start_server(port=port)
    except Exception as e:
        click.echo(f"Error deploying app: {e}")


if __name__ == "__main__":
    cli()  # Ensures the CLI is callable when executed directly
