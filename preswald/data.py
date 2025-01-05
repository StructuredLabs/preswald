import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text as sql_text
import toml
import os
import json
from typing import Dict, Any, Optional
import logging
from preswald.core import connections, get_connection
from preswald.components import table

# Configure logging
logger = logging.getLogger(__name__)

def load_connection_config(config_path: str = "config.toml", secrets_path: str = "secrets.toml") -> Dict[str, Any]:
    """
    Load connection configuration from config.toml and secrets.toml.
    
    The configuration format should be:
    [connections.my_connection]
    type = "postgres"  # or "mysql", "csv", "json", "parquet"
    host = "localhost"
    port = 5432
    dbname = "mydb"
    user = "user"
    # password comes from secrets.toml
    
    [connections.my_csv]
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
            secret_connections = secrets.get('connections', {})
            config_connections = config.get('connections', {})
            
            # Merge secrets into each connection config
            for conn_name, conn_secrets in secret_connections.items():
                if conn_name in config_connections:
                    config_connections[conn_name].update(conn_secrets)
    
    return config.get('connections', {})

def connect(source: str = None, name: Optional[str] = None, config_path: str = "config.toml") -> str:
    """
    Connect to a data source using configuration from config.toml.
    
    Args:
        source (str, optional): Direct source path or connection string. If None, uses config.
        name (str, optional): Name for the connection. If None, auto-generated.
        config_path (str): Path to config file. Defaults to "config.toml".
    
    Returns:
        str: Name of the created connection
    """
    if name is None:
        name = f"connection_{len(connections) + 1}"

    try:
        logger.info(f"[CONNECT] Attempting to connect with source: {source}")
        
        # Load config if no direct source provided
        if source is None:
            logger.info("[CONNECT] No source provided, loading from config...")
            config = load_connection_config(config_path)
            source_type = config.get('default_source', 'csv')
            source_config = config.get(source_type, {})
            logger.info(f"[CONNECT] Loaded config: {config}")
            
            if source_type == 'postgres':
                # Build connection string from config
                user = source_config.get('user', 'postgres')
                password = source_config.get('password', '')
                host = source_config.get('host', 'localhost')
                port = source_config.get('port', 5432)
                dbname = source_config.get('dbname', 'postgres')
                source = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
                logger.info(f"[CONNECT] Built PostgreSQL connection string: {source}")
            
            elif source_type == 'mysql':
                user = source_config.get('user', 'root')
                password = source_config.get('password', '')
                host = source_config.get('host', 'localhost')
                port = source_config.get('port', 3306)
                dbname = source_config.get('dbname', '')
                source = f"mysql://{user}:{password}@{host}:{port}/{dbname}"
            
            elif source_type == 'csv':
                source = source_config.get('path')
            
            elif source_type == 'json':
                source = source_config.get('url') or source_config.get('path')
            
            elif source_type == 'parquet':
                source = source_config.get('path')
            
            else:
                raise ValueError(f"Unsupported data source type: {source_type}")

        if source is None:
            raise ValueError("No data source specified in config or parameters")

        # Connect based on source type
        if isinstance(source, str):
            logger.info(f"[CONNECT] Attempting connection to source: {source}")
            
            # Try to create database engine first if it looks like a connection string
            if any(prefix in source.lower() for prefix in ['postgresql://', 'postgres://', 'mysql://']):
                logger.info("[CONNECT] Detected database connection string")
                try:
                    logger.info("[CONNECT] Creating SQLAlchemy engine...")
                    engine = create_engine(source)
                    logger.info("[CONNECT] Engine created, testing connection...")
                    
                    # Test the connection
                    with engine.connect() as conn:
                        logger.info("[CONNECT] Testing connection with SELECT 1...")
                        conn.execute(sql_text("SELECT 1"))
                        logger.info("[CONNECT] Connection test successful")
                    
                    logger.info("[CONNECT] Storing connection in registry...")
                    connections[name] = engine
                    logger.info("[CONNECT] Successfully established database connection")
                    return name
                except Exception as e:
                    logger.error(f"[CONNECT] Database connection error: {str(e)}")
                    raise
            
            # If not a database connection, try file formats
            logger.info("[CONNECT] Checking file formats...")
            if source.endswith('.csv'):
                logger.info("[CONNECT] Detected CSV source")
                connections[name] = pd.read_csv(source)
            elif source.endswith('.json') or source.startswith('http'):
                logger.info("[CONNECT] Detected JSON source")
                connections[name] = pd.read_json(source)
            elif source.endswith('.parquet'):
                logger.info("[CONNECT] Detected Parquet source")
                connections[name] = pd.read_parquet(source)
            else:
                logger.error(f"[CONNECT] Unsupported source format: {source}")
                raise ValueError(f"Unsupported data source format: {source}")
        else:
            raise ValueError("Source must be a string")

        logger.info(f"[CONNECT] Successfully created connection '{name}' to {source}")
        return name

    except Exception as e:
        logger.error(f"[CONNECT] Failed to connect to source '{source}': {e}")
        raise RuntimeError(f"Connection failed: {str(e)}")

def view(connection_name: str, limit: int = 100):
    """
    Render a preview of the data from a connection using the table component.
    
    Args:
        connection_name (str): The name of the data connection.
        limit (int): Maximum number of rows to display in the table.
    """
    connection = get_connection(connection_name)
    
    try:
        if isinstance(connection, pd.DataFrame):
            return table(connection.head(limit))
            
        elif hasattr(connection, 'connect'):  # SQLAlchemy engine
            # Get list of tables
            with connection.connect() as conn:
                # First try to get all tables
                try:
                    query = sql_text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                    tables_df = pd.read_sql_query(query, conn)
                    
                    if len(tables_df) == 0:
                        return table([], title="No tables found in the database.")
                    
                    # Create table components for each table
                    for table_name in tables_df['table_name']:
                        query = sql_text(f"SELECT * FROM {table_name} LIMIT {limit}")
                        try:
                            table_df = pd.read_sql_query(query, conn)
                            table(table_df, title=table_name)
                        except Exception as e:
                            logger.error(f"Error fetching data from table {table_name}: {e}")
                            table([], title=f"{table_name} - Error: {str(e)}")
                    
                except Exception as e:
                    logger.error(f"Error listing tables: {e}")
                    # If we can't list tables, try a simple SELECT
                    try:
                        query = sql_text("SELECT 1")
                        test_df = pd.read_sql_query(query, conn)
                        return table([], title="Connected to database successfully, but no data to display.")
                    except Exception as e:
                        logger.error(f"Error testing connection: {e}")
                        return table([], title=f"Error connecting to database: {str(e)}")
        else:
            raise TypeError(f"Connection '{connection_name}' does not contain viewable data")
    except Exception as e:
        logger.error(f"Error viewing connection '{connection_name}': {e}")
        return table([], title=f"Error: {str(e)}")

def query(connection_name: str, sql_query: str) -> pd.DataFrame:
    """
    Execute a SQL query on a database connection and return the result as a DataFrame.
    
    Args:
        connection_name (str): The name of the database connection.
        sql_query (str): The SQL query to execute.
    Returns:
        pd.DataFrame: Query results as a pandas DataFrame.
    """
    connection = get_connection(connection_name)
    
    if not hasattr(connection, 'connect'):
        raise TypeError(f"Connection '{connection_name}' is not a database connection")
    
    try:
        with connection.connect() as conn:
            # Convert the query string to a SQLAlchemy text object
            query_obj = sql_text(sql_query)
            return pd.read_sql_query(query_obj, conn)
    except Exception as e:
        logger.error(f"Error executing query on '{connection_name}': {e}")
        raise

def summary(connection_name: str):
    """
    Generate a summary of the data from a connection.
    
    Args:
        connection_name (str): The name of the data connection.
    Returns:
        dict: Table component containing the data summary.
    """
    connection = get_connection(connection_name)
    
    if isinstance(connection, pd.DataFrame):
        summary_df = connection.describe(include='all')
        return table(summary_df, title="Data Summary")
    else:
        raise TypeError(f"Connection '{connection_name}' does not contain tabular data")

def save(connection_name: str, file_path: str, format: str = "csv") -> str:
    """
    Save data from a connection to a file.
    
    Args:
        connection_name (str): The name of the data connection.
        file_path (str): Path to save the file.
        format (str): Format to save the data in ('csv', 'json', 'parquet').
    Returns:
        str: Success message.
    """
    connection = get_connection(connection_name)
    
    if not isinstance(connection, pd.DataFrame):
        raise TypeError(f"Connection '{connection_name}' does not contain tabular data")
    
    try:
        if format == "csv":
            connection.to_csv(file_path, index=False)
        elif format == "json":
            connection.to_json(file_path, orient="records")
        elif format == "parquet":
            connection.to_parquet(file_path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return f"Data saved to {file_path} in {format} format"
    except Exception as e:
        logger.error(f"Error saving data from '{connection_name}' to {file_path}: {e}")
        raise

def load(file_path: str, name: Optional[str] = None) -> str:
    """
    Load data from a file and store it as a new connection.
    
    Args:
        file_path (str): Path to the file.
        name (str, optional): Name for the new connection.
    Returns:
        str: The name of the created connection.
    """
    return connect(source=file_path, name=name)
