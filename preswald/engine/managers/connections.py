import logging
import os
from io import StringIO
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import pandas as pd
import requests
import toml
from sqlalchemy import create_engine, inspect

logger = logging.getLogger(__name__)


class ConnectionsManager:
    """
    A class to manage and parse connections from configuration files.
    This class handles both PostgreSQL and CSV connections, extracting their
    schemas and metadata.
    """

    def __init__(self, config_path: str, secrets_path: Optional[str] = None):
        """
        Initialize the ConnectionsManager.

        Args:
            config_path (str): Path to the preswald.toml file
            secrets_path (Optional[str]): Path to the secrets.toml file
        """
        self.config_path = config_path
        self.secrets_path = secrets_path
        self.config: Dict = {}
        self.secrets: Dict = {}
        self._load_config_files()

    def _load_config_files(self) -> None:
        """Load configuration and secrets files."""
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Config file not found at: {self.config_path}")

            self.config = toml.load(self.config_path)
            logger.info("Successfully loaded preswald.toml")

            if self.secrets_path and os.path.exists(self.secrets_path):
                self.secrets = toml.load(self.secrets_path)
                logger.info("Successfully loaded secrets.toml")

        except Exception as e:
            logger.error(f"Error loading configuration files: {e!s}")
            raise

    def get_connections(self) -> List[Dict[str, Any]]:
        """
        Get all connections with their metadata.

        Returns:
            List[Dict[str, Any]]: List of connection information dictionaries
        """
        connection_list = []

        if "data" not in self.config:
            logger.warning("No 'data' section found in config file")
            return connection_list

        for key, value in self.config["data"].items():
            try:
                if not isinstance(value, dict):
                    logger.warning(f"Skipping non-dict connection config: {key}")
                    continue

                connection = self._parse_connection(key, value)
                if connection:
                    connection_list.append(connection)

            except Exception as e:
                logger.error(f"Error processing connection {key}: {e!s}")
                # Add error connection info
                if "type" in value:
                    connection_list.append(
                        {
                            "name": key,
                            "type": value["type"],
                            "details": str(value),
                            "status": "error",
                            "metadata": {"error": str(e)},
                        }
                    )

        return connection_list

    def _parse_connection(self, key: str, value: Dict) -> Optional[Dict[str, Any]]:
        """
        Parse a single connection configuration.

        Args:
            key (str): Connection key/name
            value (Dict): Connection configuration

        Returns:
            Optional[Dict[str, Any]]: Connection information or None if invalid
        """
        try:
            # PostgreSQL Connection
            if self._is_postgres_connection(value):
                return self._parse_postgres_connection(key, value)

            # CSV Connection
            elif self._is_csv_connection(value):
                return self._parse_csv_connection(key, value)

            else:
                logger.warning(f"Unknown connection type for {key}")
                return None

        except Exception as e:
            logger.error(f"Error parsing connection {key}: {e!s}")
            raise

    def _is_postgres_connection(self, value: Dict) -> bool:
        """Check if the connection is PostgreSQL type."""
        return (
            all(field in value for field in ["host", "port", "dbname"])
            and value.get("port") == 5432
        )

    def _is_csv_connection(self, value: Dict) -> bool:
        """Check if the connection is CSV type."""
        return "path" in value and str(value["path"]).endswith(".csv")

    def _parse_postgres_connection(self, key: str, value: Dict) -> Dict[str, Any]:
        """Parse PostgreSQL connection and get its metadata."""
        details = {
            "host": value.get("host", ""),
            "port": value.get("port", ""),
            "dbname": value.get("dbname", ""),
            "user": value.get("user", ""),
        }

        metadata = {}
        try:
            password = self._get_postgres_password(key)
            if not password:
                metadata = {"error": "No password entry found in secrets.toml"}
                return self._create_connection_dict(
                    key, "PostgreSQL", details, "configured", metadata
                )

            metadata = self._get_postgres_metadata(details, password)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error getting PostgreSQL metadata for {key}: {error_msg}")
            if "password" in error_msg.lower():
                metadata = {
                    "error": "Invalid password. Please check your credentials in secrets.toml"
                }
            else:
                metadata = {"error": f"Could not connect to database: {error_msg}"}

        return self._create_connection_dict(
            key, "PostgreSQL", details, "configured", metadata
        )

    def _get_postgres_password(self, key: str) -> Optional[str]:
        """Get PostgreSQL password from secrets."""
        return self.secrets.get("data", {}).get(key, {}).get("password")

    def _get_postgres_metadata(
        self, details: Dict[str, str], password: str
    ) -> Dict[str, Any]:
        """Get PostgreSQL connection metadata including schema information."""
        password = quote_plus(password)
        conn_str = f"postgresql://{details['user']}:{password}@{details['host']}:{details['port']}/{details['dbname']}"
        logger.info(f"Connecting to PostgreSQL with connection string: {conn_str}")
        engine = create_engine(conn_str)
        with engine.connect():
            inspector = inspect(engine)
            schemas = inspector.get_schema_names()
            tables_info = {}

            for schema in schemas:
                tables = inspector.get_table_names(schema=schema)
                tables_info[schema] = {}

                for table in tables:
                    columns = inspector.get_columns(table, schema=schema)
                    tables_info[schema][table] = {
                        "columns": [
                            {
                                "name": col["name"],
                                "type": str(col["type"]),
                                "nullable": col["nullable"],
                            }
                            for col in columns
                        ]
                    }

            return {
                "database_name": details["dbname"],
                "schemas": tables_info,
                "total_tables": sum(len(tables) for tables in tables_info.values()),
            }

    def _parse_csv_connection(self, key: str, value: Dict) -> Dict[str, Any]:
        """Parse CSV connection and get its metadata."""
        file_path = value.get("path", "")
        details = {"path": file_path}
        metadata = {}

        try:
            if file_path.startswith(("http://", "https://")):
                metadata = self._get_remote_csv_metadata(file_path)
            else:
                metadata = self._get_local_csv_metadata(file_path)

        except requests.exceptions.RequestException as e:
            metadata = {
                "error": f"Could not fetch remote file: {e!s}",
                "source": "remote",
            }
        except Exception as e:
            metadata = {"error": f"Could not read file: {e!s}", "source": "unknown"}

        return self._create_connection_dict(key, "CSV", details, "configured", metadata)

    def _get_remote_csv_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get metadata for remote CSV file."""
        response = requests.get(file_path)
        response.raise_for_status()

        csv_content = StringIO(response.text)
        df = pd.read_csv(csv_content, nrows=5)

        total_rows = len(response.text.splitlines()) - 1
        file_size_mb = len(response.content) / (1024 * 1024)

        return self._create_csv_metadata(df, total_rows, file_size_mb, "remote")

    def _get_local_csv_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get metadata for local CSV file."""
        if not os.path.exists(file_path):
            return {"error": "File not found", "source": "local"}

        df = pd.read_csv(file_path, nrows=5)
        total_rows = sum(1 for _ in open(file_path)) - 1
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

        return self._create_csv_metadata(df, total_rows, file_size_mb, "local")

    def _create_csv_metadata(
        self, df: pd.DataFrame, total_rows: int, file_size_mb: float, source: str
    ) -> Dict[str, Any]:
        """Create metadata dictionary for CSV files."""
        return {
            "columns": [
                {
                    "name": col,
                    "type": str(df[col].dtype),
                    "sample_values": [str(val) for val in df[col].head().tolist()],
                }
                for col in df.columns
            ],
            "total_rows": total_rows,
            "total_columns": len(df.columns),
            "file_size": f"{file_size_mb:.2f} MB",
            "source": source,
        }

    @staticmethod
    def _create_connection_dict(
        name: str,
        conn_type: str,
        details: Dict[str, Any],
        status: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a standardized connection information dictionary."""
        return {
            "name": name,
            "type": conn_type,
            "details": ", ".join(f"{k}: {v}" for k, v in details.items() if v),
            "status": status,
            "metadata": metadata,
        }
