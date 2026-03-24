import logging

import pandas as pd

from preswald.engine.service import PreswaldService


# Configure logging
logger = logging.getLogger(__name__)

# Track whether connect() has been called to avoid duplicate table registration
_connected = False


def connect():
    """
    Connect to all listed data sources in preswald.toml.

    Safe to call multiple times -- subsequent calls are no-ops unless
    the underlying data sources have changed.
    """
    global _connected
    try:
        service = PreswaldService.get_instance()
        if _connected and service.data_manager and service.data_manager.sources:
            logger.debug("Data sources already connected, skipping re-initialization")
            return service.data_manager.duckdb_conn

        source_names, duckdb_conn = service.data_manager.connect()
        _connected = True
        logger.info(f"Successfully connected to data sources: {source_names}")
        return duckdb_conn
    except Exception as e:
        logger.error(f"Error connecting to datasources: {e}")


def query(sql: str, source_name: str) -> pd.DataFrame:
    """
    Query a data source using sql from preswald.toml by name
    """
    try:
        service = PreswaldService.get_instance()
        df_result = service.data_manager.query(sql, source_name)
        logger.info(f"Successfully queried data source: {source_name}")
        return df_result
    except Exception as e:
        logger.error(f"Error querying data source: {e}")


def get_df(source_name: str, table_name: str | None = None) -> pd.DataFrame:
    """
    Get a dataframe from the named data source from preswald.toml
    If the source is a database/has multiple tables, you must specify a table_name
    """
    try:
        service = PreswaldService.get_instance()
        df_result = service.data_manager.get_df(source_name, table_name)
        logger.info(f"Successfully got a dataframe from data source: {source_name}")
        return df_result
    except Exception as e:
        logger.error(f"Error getting a dataframe from data source: {e}")
