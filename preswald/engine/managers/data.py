import json
import logging
import os
import uuid
from dataclasses import dataclass
from typing import Any

import duckdb
import pandas as pd
import requests
import toml
from requests.auth import HTTPBasicAuth


logger = logging.getLogger(__name__)


# Database Configs ############################################################
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


# File Configs ################################################################
@dataclass
class CSVConfig:
    path: str


@dataclass
class JSONConfig:
    path: str
    record_path: str | None = None
    flatten: bool = True


@dataclass
class ParquetConfig:
    path: str
    columns: list[str] | None


# API Configs #################################################################
@dataclass
class APIConfig:
    """Configuration for API connection"""

    url: str  #  URL of the API
    method: str = "GET"  # HTTP method (GET, POST, etc.)
    headers: dict[str, str] | None = None
    params: dict[str, Any] | None = None  # Query parameters
    auth: dict[str, str] | None = None  # Authentication (API key, Bearer token)
    pagination: dict[str, Any] | None = None


# S3 Configs ##################################################################
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
        self._table_name = f"csv_{uuid.uuid4().hex[:8]}"
        self._duckdb.execute(f"""
            CREATE TABLE {self._table_name} AS
            SELECT * FROM read_csv_auto('{self.path}',
                header=true,
                auto_detect=true,
                ignore_errors=true,
                normalize_names=false,
                sample_size=-1,
                all_varchar=true
            )
        """)

    def query(self, sql: str) -> pd.DataFrame:
        # Replace source name with actual table name in query
        sql = sql.replace(self.name, self._table_name)
        return self._duckdb.execute(sql).df()

    def to_df(self) -> pd.DataFrame:
        """Get entire CSV as a DataFrame"""
        return self._duckdb.execute(f"SELECT * FROM {self._table_name}").df()


class JSONSource(DataSource):
    def __init__(
        self, name: str, config: JSONConfig, duckdb_conn: duckdb.DuckDBPyConnection
    ):
        super().__init__(name, duckdb_conn)
        df = _load_json_source(config.__dict__)  # noqa: F841
        self._table_name = f"json_{uuid.uuid4().hex[:8]}"
        self._duckdb.execute(f"CREATE TABLE {self._table_name} AS SELECT * FROM df")

    def query(self, sql: str) -> pd.DataFrame:
        return self._duckdb.execute(sql.replace(self.name, self._table_name)).df()

    def to_df(self) -> pd.DataFrame:
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
        self._table_name = f"api_{uuid.uuid4().hex[:8]}"
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


class ParquetSource(DataSource):
    def __init__(
        self, name: str, config: ParquetConfig, duckdb_conn: duckdb.DuckDBPyConnection
    ):
        super().__init__(name, duckdb_conn)
        self.path = config.path
        self.columns = config.columns
        self._table_name = f"parquet_{uuid.uuid4().hex[:8]}"

        try:
            # Load Parquet using DuckDB
            if self.columns:
                column_str = ", ".join(f'"{col}"' for col in self.columns)
                self._duckdb.execute(f"""
                    CREATE TABLE {self._table_name} AS
                    SELECT {column_str}
                    FROM read_parquet('{self.path}')
                """)
            else:
                self._duckdb.execute(f"""
                    CREATE TABLE {self._table_name} AS
                    SELECT * FROM read_parquet('{self.path}')
                """)
        except Exception as e:
            raise Exception(
                f"Failed to load parquet file '{self.path}' using DuckDB: {e!s}"
            ) from e

    def query(self, sql: str) -> pd.DataFrame:
        query = sql.replace(self.name, self._table_name)
        return self._duckdb.execute(query).df()

    def to_df(self) -> pd.DataFrame:
        return self._duckdb.execute(f"SELECT * FROM {self._table_name}").df()


class DataManager:
    def __init__(self, preswald_path: str, secrets_path: str | None = None):
        self.preswald_path = preswald_path
        self.secrets_path = secrets_path
        self.sources: dict[str, DataSource] = {}
        self.sources_cache: dict[str, dict] = {}  # Cache of source configurations
        self.duckdb_conn = duckdb.connect(":memory:")

    def connect(self):  # noqa: C901
        """Initialize all data sources from config"""
        # Useful debugging query - Log final DuckDB state
        # tables_df = self.duckdb_conn.execute("""
        #     SELECT
        #         table_name,
        #         column_count,
        #         estimated_size as size_b
        #     FROM duckdb_tables()
        # """).df()

        # logger.info(f"Current DuckDB state - {len(tables_df)} tables:")
        # for _, row in tables_df.iterrows():
        #     logger.info(
        #         f"Table: {row['table_name']}, Columns: {row['column_count']}, Estimated Size: {row['size_b']:.2f}B"
        #     )

        config = self._load_sources()

        # Only process sources that are new or have changed
        for name, source_config in config.items():
            if "type" not in source_config:
                continue

            if not self._has_source_changed(name, source_config):
                logger.debug(f"Skipping unchanged source: {name}")
                continue

            if name in self.sources:
                self._drop_source_table(self.sources[name])

            source_type = source_config["type"]
            logger.info(f"Initializing/updating source: {name} ({source_type})")

            try:
                if source_type == "csv":
                    cfg = CSVConfig(path=source_config["path"])
                    self.sources[name] = CSVSource(name, cfg, self.duckdb_conn)

                elif source_type == "json":
                    cfg = JSONConfig(
                        path=source_config["path"],
                        record_path=source_config.get("record_path"),
                        flatten=source_config.get("flatten", True),
                    )
                    self.sources[name] = JSONSource(name, cfg, self.duckdb_conn)

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

                elif source_type == "parquet":
                    cfg = ParquetConfig(
                        path=source_config["path"],
                        columns=source_config.get("columns"),
                    )
                    self.sources[name] = ParquetSource(name, cfg, self.duckdb_conn)

                # Cache the config after successful initialization
                self.sources_cache[name] = source_config

            except Exception as e:
                logger.error(f"Error initializing {source_type} source '{name}': {e}")
                continue
        return self.sources.keys(), self.duckdb_conn

    def query(self, sql: str, source_name: str) -> pd.DataFrame:
        """Query a specific data source"""
        source = self._get_or_create_source(source_name)
        return source.query(sql)

    def get_df(self, source_name: str, table_name: str | None = None) -> pd.DataFrame:
        """Get entire source as DataFrame"""
        source = self._get_or_create_source(source_name)

        if isinstance(source, PostgresSource):
            if table_name is None:
                raise ValueError("table_name is required for Postgres sources")
            return source.to_df(table_name)
        return source.to_df()

    def _get_or_create_source(self, source_name: str) -> DataSource:
        """Get an existing source or create a new one from a file path."""
        if source_name not in self.sources:
            # check if source_name is a valid file path
            if os.path.exists(source_name):
                if source_name.endswith(".csv"):
                    cfg = CSVConfig(path=source_name)
                    self.sources[source_name] = CSVSource(
                        source_name, cfg, self.duckdb_conn
                    )
                elif source_name.endswith(".json"):
                    cfg = JSONConfig(path=source_name)
                    self.sources[source_name] = JSONSource(
                        source_name, cfg, self.duckdb_conn
                    )
                elif source_name.endswith(".parquet"):
                    cfg = ParquetConfig(path=source_name)
                    self.sources[source_name] = ParquetSource(
                        source_name, cfg, self.duckdb_conn
                    )
                else:
                    raise ValueError(f"Unsupported file type: {source_name}")
            else:
                raise ValueError(f"Unknown source: {source_name}")

        return self.sources[source_name]

    def _has_source_changed(self, name: str, config: dict) -> bool:
        """Check if a source's configuration has changed"""
        if name not in self.sources_cache:
            return True
        return self.sources_cache[name] != config

    def _drop_source_table(self, source: DataSource) -> None:
        """Drop the DuckDB table for a source if it exists"""
        if isinstance(
            source, CSVSource | JSONSource | S3CSVSource | APISource | ParquetSource
        ):
            logger.info(f"Dropping table {source._table_name}")
            self.duckdb_conn.execute(f"DROP TABLE IF EXISTS {source._table_name}")

    def _load_sources(self) -> dict[str, Any]:
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


def _load_json_source(config: dict[str, Any]) -> pd.DataFrame:
    path = config["path"]
    record_path = config.get("record_path")
    flatten = config.get("flatten", True)

    # Open and load the JSON file
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed JSON in file '{path}': {e}") from e
    except Exception as e:
        raise ValueError(f"Error reading JSON file '{path}': {e}") from e

    # Apply record_path if provided
    if record_path:
        try:
            data = data[record_path]
        except (KeyError, TypeError) as e:
            raise ValueError(
                f"Invalid record_path '{record_path}' for JSON file '{path}': {e}"
            ) from e

    # Normalize or convert data if "flatten"
    try:
        if flatten:
            return pd.json_normalize(data, sep=".")
        else:
            return pd.DataFrame(data)
    except Exception as e:
        raise ValueError(
            f"Error converting JSON data from file '{path}' to DataFrame: {e}"
        ) from e
