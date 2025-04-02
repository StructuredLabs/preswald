import logging
import os
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

import duckdb
import pandas as pd
import requests
import toml
from requests.auth import HTTPBasicAuth


logger = logging.getLogger(__name__)


@dataclass
class ClickhouseConfig:
    """Configuration for Clickhouse connection"""

    host: str
    port: int
    database: str
    user: str
    password: str
    secure: bool = False  # Whether to use HTTPS/SSL
    verify: bool = True  # Whether to verify SSL certificate


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


@dataclass
class APIConfig:
    """Configuration for API connection"""

    url: str  #  URL of the API
    method: str = "GET"  # HTTP method (GET, POST, etc.)
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None  # Query parameters
    auth: Optional[Dict[str, str]] = None  # Authentication (API key, Bearer token)
    pagination: Optional[Dict[str, Any]] = None


@dataclass
class S3CSVConfig:
    s3_endpoint: str
    s3_region: str
    s3_access_key_id: str
    s3_secret_access_key: str
    path: str
    s3_use_ssl: bool = False
    s3_url_style: str = "path"


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


class S3CSVSource(DataSource):
    def __init__(
        self, name: str, config: S3CSVConfig, duckdb_conn: duckdb.DuckDBPyConnection
    ):
        super().__init__(name, duckdb_conn)
        self.config = config

        # Initialize httpfs extension
        self._duckdb.execute("INSTALL httpfs;")
        self._duckdb.execute("LOAD httpfs;")

        use_ssl = "true" if config.s3_use_ssl else "false"

        self._conn_string = (
            f"?s3_endpoint={config.s3_endpoint}"
            f"&s3_region={config.s3_region}"
            f"&s3_use_ssl={use_ssl}"
            f"&s3_access_key_id={config.s3_access_key_id}"
            f"&s3_secret_access_key={config.s3_secret_access_key}"
            f"&s3_url_style={config.s3_url_style}"
        )

        # Create a table in DuckDB for this CSV
        self._table_name = f"s3_{name}_{uuid.uuid4().hex[:8]}"
        self._duckdb.execute(f"""
            CREATE TABLE {self._table_name} AS
            SELECT * FROM read_csv_auto('{config.path}{self._conn_string}')
        """)

    def query(self, sql: str) -> pd.DataFrame:
        sql = sql.replace(self.name, self._table_name)
        return self._duckdb.execute(sql).df()

    def to_df(self) -> pd.DataFrame:
        """Get entire CSV as a DataFrame"""
        return self._duckdb.execute(f"SELECT * FROM {self._table_name}").df()


class CSVSource(DataSource):
    def __init__(
        self, name: str, config: CSVConfig, duckdb_conn: duckdb.DuckDBPyConnection
    ):
        super().__init__(name, duckdb_conn)
        self.path = config.path

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
        self._duckdb.execute(f"CALL postgres_attach('{self._conn_string}')")
        result = self._duckdb.execute(sql).df()
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


class ClickhouseSource(DataSource):
    def __init__(
        self,
        name: str,
        config: ClickhouseConfig,
        duckdb_conn: duckdb.DuckDBPyConnection,
    ):
        super().__init__(name, duckdb_conn)
        self.config = config

        # Initialize clickhouse_scanner extension
        self._duckdb.execute("INSTALL chsql from community;")
        self._duckdb.execute("LOAD chsql;")

        # Construct connection string
        protocol = "https" if self.config.secure else "http"
        self._conn_string = (
            f"{protocol}://{config.user}:{config.password}"
            f"@{config.host}:{config.port}"
            f"/{config.database}"
            f"?verify={'true' if config.verify else 'false'}"
        )

        self._server_url = f"{protocol}://{config.host}:{config.port}"

    def query(self, sql: str) -> pd.DataFrame:
        """Execute a SQL query against Clickhouse"""
        try:
            wrapped_sql = f"SELECT * FROM ch_scan('{sql}', '{self._server_url}', user := 'default')"
            result = self._duckdb.execute(wrapped_sql).df()
            return result
        except Exception as e:
            raise Exception(f"Error executing Clickhouse query: {e!s}") from e

    def to_df(self, table_name: str) -> pd.DataFrame:
        """Get entire table as a DataFrame"""
        try:
            wrapped_sql = f"SELECT * FROM ch_scan('SELECT * FROM {table_name}', '{self._server_url}', user := 'default')"
            result = self._duckdb.execute(wrapped_sql).df()
            return result

        except Exception as e:
            # Clean up views if they exist
            logger.error(f"Error reading table {table_name}: {e}")
            raise

    def __del__(self):
        """Cleanup when the source is destroyed"""
        try:
            # Clean up the CHSQL connection
            self._duckdb.execute("CALL chsql_cleanup();")
        except:  # noqa: E722
            pass  # Ignore cleanup errors on destruction


class APISource(DataSource):
    def __init__(
        self, name: str, config: APIConfig, duckdb_conn: duckdb.DuckDBPyConnection
    ):
        super().__init__(name, duckdb_conn)
        self.config = config

        # Create a table in db
        self._table_name = f"api_{name}_{uuid.uuid4().hex[:8]}"
        self._load_data_into_duckdb()

    def _load_data_into_duckdb(self):
        """Fetch data from the API and load it into DuckDB"""
        try:
            # API request
            response = self._make_api_request()
            data = response.json()

            # Convert JSON to DF
            df = pd.json_normalize(data)  # noqa: F841

            # Create a table in DB
            self._duckdb.execute(f"""
                CREATE TABLE {self._table_name} AS
                SELECT * FROM df
            """)
        except Exception as e:
            logger.error(f"Error loading API data into DuckDB: {e}")
            raise

    def _make_api_request(self):
        """Make an API request based on the configuration"""
        try:
            auth = None
            if self.config.auth:
                if "type" in self.config.auth and self.config.auth["type"] == "basic":
                    auth = HTTPBasicAuth(
                        self.config.auth["username"], self.config.auth["password"]
                    )
                elif (
                    "type" in self.config.auth and self.config.auth["type"] == "bearer"
                ):
                    headers = self.config.headers or {}
                    headers["Authorization"] = f"Bearer {self.config.auth['token']}"

            response = requests.request(
                method=self.config.method,
                url=self.config.url,
                headers=self.config.headers,
                params=self.config.params,
                auth=auth,
            )
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            raise

    def query(self, sql: str) -> pd.DataFrame:
        """Query the API data using DuckDB"""
        sql = sql.replace(self.name, self._table_name)
        return self._duckdb.execute(sql).df()

    def to_df(self) -> pd.DataFrame:
        """Get the entire API data as a DataFrame"""
        return self._duckdb.execute(f"SELECT * FROM {self._table_name}").df()


class DataManager:
    def __init__(self, preswald_path: str, secrets_path: Optional[str] = None):
        self.preswald_path = preswald_path
        self.secrets_path = secrets_path
        self.sources: Dict[str, DataSource] = {}
        self.duckdb_conn = duckdb.connect(":memory:")

    def connect(self):
        """Initialize all data sources from config"""
        config = self._load_sources()
        for name, source_config in config.items():
            if "type" not in source_config:
                continue

            source_type = source_config["type"]

            try:
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

                elif source_type == "clickhouse":
                    cfg = ClickhouseConfig(
                        host=source_config["host"],
                        port=source_config["port"],
                        database=source_config["database"],
                        user=source_config["user"],
                        password=source_config["password"],
                        secure=source_config.get("secure", False),
                        verify=source_config.get("verify", True),
                    )
                    self.sources[name] = ClickhouseSource(name, cfg, self.duckdb_conn)

                elif source_type == "api":
                    cfg = APIConfig(
                        url=source_config["url"],
                        method=source_config.get("method", "GET"),
                        headers=source_config.get("headers"),
                        params=source_config.get("params"),
                        auth=source_config.get("auth"),
                        pagination=source_config.get("pagination"),
                    )
                    self.sources[name] = APISource(name, cfg, self.duckdb_conn)

                elif source_type == "s3csv":
                    cfg = S3CSVConfig(
                        s3_endpoint=source_config["s3_endpoint"],
                        s3_region=source_config["s3_region"],
                        s3_access_key_id=source_config["s3_access_key_id"],
                        s3_secret_access_key=source_config["s3_secret_access_key"],
                        path=source_config["path"],
                        s3_use_ssl=source_config.get("s3_use_ssl", False),
                        s3_url_style=source_config.get("s3_url_style", "path"),
                    )
                    self.sources[name] = S3CSVSource(name, cfg, self.duckdb_conn)

            except Exception as e:
                logger.error(f"Error initializing {source_type} source '{name}': {e}")
                continue
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
