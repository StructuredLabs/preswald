import logging

import pandas as pd

from preswald.engine.service import PreswaldService

from .components import table


# Configure logging
logger = logging.getLogger(__name__)


def connect():
    """
    Connect to all listed data sources in preswald.toml
    """
    try:
        service = PreswaldService.get_instance()
        source_names, duckdb_conn = service.data_manager.connect()
        logger.info(f"Successfully connected to data sources: {source_names}")
        # TODO: bug - getting duplicated if there are multiple clients
        return duckdb_conn
    except Exception as e:
        logger.error(f"Error connecting to datasources: {e}")


def query():
    pass


# TODO: does this work with connection name?
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
