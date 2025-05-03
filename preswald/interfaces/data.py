import logging
import time

import pandas as pd

from preswald.engine.service import PreswaldService


# Configure logging
logger = logging.getLogger(__name__)


def connect():
    """
    Connect to all listed data sources in preswald.toml

    Returns:
        A DuckDBPyConnection instance if connection is successful, otherwise None.
    """
    try:
        service = PreswaldService.get_instance()
        source_names, duckdb_conn = service.data_manager.connect()
        logger.info(f"Successfully connected to data sources: {source_names}")
        # TODO: bug - getting duplicated if there are multiple clients
        return duckdb_conn
    except Exception as e:
        logger.error(f"Error connecting to datasources: {e}")
        return None


def query(sql: str, source_name: str) -> pd.DataFrame | None:
    """
    Query a data source using sql from preswald.toml by name.

    Args:
        sql: The SQL query to run.
        source_name: The name of the data source configured in preswald.toml.

    Returns:
        A pandas DataFrame if successful, otherwise None
    """
    try:
        service = PreswaldService.get_instance()
        # Measure and log query execution time for performance monitoring
        start_time = time.time()
        df_result = service.data_manager.query(sql, source_name)
        elapsed_time = time.time() - start_time
        logger.info(f"Successfully queried data source: {source_name}")
        return df_result
    except Exception as e:
        logger.error(f"Error querying data source: {e}")
        return None


def get_df(source_name: str, table_name: str | None = None) -> pd.DataFrame:
    """
    Get a dataframe from the named data source from preswald.toml
    If the source is a database/has multiple tables, you must specify a table_name

    Args:
        source_name: The name of the configured data source.
        table_name: Optional; name of the table to load if the source has multiple tables.

    Returns:
        A pandas DataFrame if successful, otherwise None.
    """
    try:
        service = PreswaldService.get_instance()
        df_result = service.data_manager.get_df(source_name, table_name)
        logger.info(f"Successfully got a dataframe from data source: {source_name}")
        return df_result
    except Exception as e:
        logger.error(f"Error getting a dataframe from data source: {e}")
        return None
