import logging
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import duckdb
import pandas as pd
import toml


logger = logging.getLogger(__name__)


@dataclass
class PostgresConfig:
    host: str
    port: int
    dbname: str
    user: str
    password: str


@dataclass
class CSVConfig:
    path: str


class DataSource:
    """Base class for all data sources"""

    def __init__(self, name: str, duckdb_conn: duckdb.DuckDBPyConnection):
        self.name = name
        self._duckdb = duckdb_conn

    def query(self, sql: str) -> pd.DataFrame:
        raise NotImplementedError

    def to_df(self) -> pd.DataFrame:
        """Get entire source as a DataFrame"""
        raise NotImplementedError


class CSVSource(DataSource):
    def __init__(
        self, name: str, config: CSVConfig, duckdb_conn: duckdb.DuckDBPyConnection
    ):
        super().__init__(name, duckdb_conn)
        self.path = Path(config.path)

        # Create a table in DuckDB for this CSV
        self._table_name = f"csv_{name}_{uuid.uuid4().hex[:8]}"
        self._duckdb.execute(f"""
            CREATE TABLE {self._table_name} AS
            SELECT * FROM read_csv_auto('{self.path}')
        """)

    def query(self, sql: str) -> pd.DataFrame:
        # Replace source name with actual table name in query
        sql = sql.replace(self.name, self._table_name)
        return self._duckdb.execute(sql).df()

    def to_df(self) -> pd.DataFrame:
        """Get entire CSV as a DataFrame"""
        return self._duckdb.execute(f"SELECT * FROM {self._table_name}").df()


class PostgresSource(DataSource):
    def __init__(
        self, name: str, config: PostgresConfig, duckdb_conn: duckdb.DuckDBPyConnection
    ):
        super().__init__(name, duckdb_conn)
        self.config = config

        # Initialize postgres_scanner extension
        self._duckdb.execute("INSTALL postgres_scanner;")
        self._duckdb.execute("LOAD postgres_scanner;")

        self._conn_string = (
            f"postgresql://{config.user}:{config.password}"
            f"@{config.host}:{config.port}/{config.dbname}"
        )

    def query(self, sql: str) -> pd.DataFrame:
        # For Postgres, we create a view for the specific query
        view_name = f"pg_view_{uuid.uuid4().hex[:8]}"

        # Extract table name from query (simplified version)
        table_name = sql.split("FROM")[1].strip().split()[0]

        self._duckdb.execute(f"""
            CREATE OR REPLACE VIEW {view_name} AS
            SELECT * FROM postgres_scan('{self._conn_string}', 'SELECT * FROM {table_name}')
        """)

        # Replace source name with view name in query
        sql = sql.replace(table_name, view_name)
        result = self._duckdb.execute(sql).df()

        # Cleanup
        self._duckdb.execute(f"DROP VIEW IF EXISTS {view_name}")
        return result

    def to_df(self, table_name: str, schema: str = "public") -> pd.DataFrame:
        """Get entire table as a DataFrame"""
        logger.info("to_df")
        try:
            view_name = f"pg_view_{uuid.uuid4().hex[:8]}"
            self._duckdb.execute(f"""
                CREATE OR REPLACE VIEW {view_name} AS
                SELECT * FROM postgres_scan(
                    '{self._conn_string}',
                    '{schema}',
                    '{table_name}'
                )
            """)
            result = self._duckdb.execute(f"SELECT * FROM {view_name}").df()
            self._duckdb.execute(f"DROP VIEW IF EXISTS {view_name}")
            return result
        except Exception as e:
            # Clean up views if they exist
            self._duckdb.execute(f"DROP VIEW IF EXISTS {view_name}")
            raise Exception(f"Error reading table {schema}.{table_name}: {e!s}") from e


class DataManager:
    def __init__(self, preswald_path: str, secrets_path: Optional[str] = None):
        self.preswald_path = preswald_path
        self.secrets_path = secrets_path
        self.sources: Dict[str, DataSource] = {}

        # TODO: efficiently manage this on-disk as well
        self.duckdb_conn = duckdb.connect(":memory:")

    def connect(self):
        """Initialize all data sources from config"""
        config = self._load_sources()
        for name, source_config in config.items():
            if "type" not in source_config:
                continue

            source_type = source_config["type"]

            # TODO: need to handle errors more gracefully here

            if source_type == "csv":
                cfg = CSVConfig(path=source_config["path"])
                self.sources[name] = CSVSource(name, cfg, self.duckdb_conn)

            elif source_type == "postgres":
                cfg = PostgresConfig(
                    host=source_config["host"],
                    port=source_config["port"],
                    dbname=source_config["dbname"],
                    user=source_config["user"],
                    password=source_config["password"],
                )
                self.sources[name] = PostgresSource(name, cfg, self.duckdb_conn)
        return self.sources.keys(), self.duckdb_conn

    def query(self, sql: str, source_name: str) -> pd.DataFrame:
        """Query a specific data source"""
        if source_name not in self.sources:
            raise ValueError(f"Unknown source: {source_name}")
        return self.sources[source_name].query(sql)

    def get_df(
        self, source_name: str, table_name: Optional[str] = None
    ) -> pd.DataFrame:
        """Get entire source as DataFrame"""
        if source_name not in self.sources:
            raise ValueError(f"Unknown source: {source_name}")

        source = self.sources[source_name]
        if isinstance(source, PostgresSource):
            if table_name is None:
                raise ValueError("table_name is required for Postgres sources")
            return source.to_df(table_name)
        return source.to_df()

    def _load_sources(self) -> Dict[str, Any]:
        """Load data sources from preswald config and secrets files."""
        try:
            if not os.path.exists(self.preswald_path):
                raise FileNotFoundError(
                    f"preswald.toml file not found at: {self.preswald_path}"
                )

            config = toml.load(self.preswald_path)
            data_config = config.get("data", {})
            logger.info("Successfully loaded preswald.toml")

            if self.secrets_path and os.path.exists(self.secrets_path):
                secrets = toml.load(self.secrets_path)
                logger.info("Successfully loaded secrets.toml")

                secret_sources = secrets.get("data", {})

                # Merge secrets into each connection config
                for name, values in secret_sources.items():
                    if name in data_config:
                        data_config[name].update(values)

            return data_config

        except Exception as e:
            logger.error(f"Error loading configuration files: {e!s}")
            raise
