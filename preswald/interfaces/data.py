import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text as sql_text
import toml
import os
import json
from typing import Dict, Any, Optional
import logging
from preswald.interfaces.components import table

# Configure logging
logger = logging.getLogger(__name__)

def load_connection_config(config_path: str = "preswald.toml", secrets_path: str = "secrets.toml") -> Dict[str, Any]:
    """
    Load connection configuration from preswald.toml and secrets.toml.
    
    The configuration format should be:
    [data.my_connection]
    type = "postgres"  # or "mysql", "csv", "json", "parquet"
    host = "localhost"
    port = 5432
    dbname = "mydb"
    user = "user"
    # password comes from secrets.toml
    
    [data.my_csv]
    type = "csv"
    path = "data/myfile.csv"
    """
    config = {}
    
    # Load main config
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = toml.load(f)
    
    # Load and merge secrets
    if os.path.exists(secrets_path):
        with open(secrets_path, 'r') as f:
            secrets = toml.load(f)
            # Get connections section from secrets
            secret_connections = secrets.get('data', {})
            config_connections = config.get('data', {})
            
            # Merge secrets into each connection config
            for conn_name, conn_secrets in secret_connections.items():
                if conn_name in config_connections:
                    config_connections[conn_name].update(conn_secrets)
    
    return config.get('connections', {})

def view(data_or_connection_name, limit: int = 100):
    """
    Render a preview of the data using the table component.
    
    Args:
        data_or_connection_name: Either a pandas DataFrame or a connection name string.
        limit (int): Maximum number of rows to display in the table.
    """
    try:
        if isinstance(data_or_connection_name, pd.DataFrame):
            return table(data_or_connection_name.head(limit))
    except Exception as e:
        logger.error(f"Error rendering data: {e}")
        return table(pd.DataFrame())
