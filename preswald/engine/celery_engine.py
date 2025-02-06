import json
import logging
import os
import tempfile
import time
from typing import Any, Dict, Optional

from celery import Celery

from .connections_manager import ConnectionsManager

logger = logging.getLogger(__name__)


class CeleryEngine:
    """
    A class to manage Celery tasks for connection parsing.
    Uses SQLite broker to avoid external Redis dependency.
    """

    def __init__(self):
        """Initialize the CeleryEngine with SQLite broker."""
        # Create temp directory for broker and results
        self.temp_dir = os.path.join(tempfile.gettempdir(), "preswald")
        os.makedirs(self.temp_dir, exist_ok=True)

        # Set up SQLite broker and backend
        broker_db = os.path.join(self.temp_dir, "celery_broker.db")
        backend_db = os.path.join(self.temp_dir, "celery_backend.db")

        self.celery_app = Celery(
            "preswald",
            broker=f"sqla+sqlite:///{broker_db}",
            backend=f"db+sqlite:///{backend_db}",
        )

        # Configure Celery
        self.celery_app.conf.update(
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
            timezone="UTC",
            enable_utc=True,
            task_track_started=True,
            task_time_limit=3600,
            worker_prefetch_multiplier=1,
            worker_max_tasks_per_child=1000,
            worker_hijack_root_logger=False,
            worker_redirect_stdouts=False,
            broker_connection_retry=True,
            broker_connection_max_retries=None,  # Retry indefinitely
        )

        # Store the latest parsing result
        self.latest_result: Dict[str, Any] = {
            "connections": [],
            "error": None,
            "timestamp": 0,
            "is_parsing": False,
        }

        # Register tasks - must be done after setting up instance variables
        @self.celery_app.task(name="preswald.parse_connections")
        def parse_connections_task(script_path: str) -> Dict[str, Any]:
            return self._parse_connections_task(script_path)

        self.parse_connections = parse_connections_task

    def get_ipc_file(self) -> str:
        """Get the IPC file path."""
        return os.path.join(self.temp_dir, f"preswald_connections_{os.getpid()}.json")

    def write_to_ipc(self, data: Dict[str, Any]) -> None:
        """Write data to IPC file."""
        try:
            ipc_file = self.get_ipc_file()
            with open(ipc_file, "w") as f:
                json.dump(data, f)
            logger.info("[Celery] Successfully wrote to IPC file: %s", ipc_file)
        except Exception as e:
            logger.error("[Celery] Error writing to IPC file: %s", str(e))

    def _parse_connections_task(self, script_path: str) -> Dict[str, Any]:
        """
        Celery task to parse all connections.

        Args:
            script_path (str): Path to the script file

        Returns:
            Dict[str, Any]: Connection parsing results
        """
        logger.info("[Celery] ====== Starting connection parsing task ======")

        try:
            # Initialize ConnectionsManager
            script_dir = os.path.dirname(script_path)
            config_path = os.path.join(script_dir, "preswald.toml")
            secrets_path = os.path.join(script_dir, "secrets.toml")

            manager = ConnectionsManager(
                config_path=config_path, secrets_path=secrets_path
            )

            # Get connections
            connections = manager.get_connections()

            # Prepare result
            result = {
                "connections": connections,
                "error": None,
                "timestamp": time.time(),
                "is_parsing": False,
            }

            # Update latest result
            self.latest_result = result

            # Write to IPC file
            self.write_to_ipc(result)
            logger.info("[Celery] ====== Task Complete ======")

            return result

        except Exception as e:
            logger.error("[Celery] ====== Task Failed ======")
            logger.error(
                "[Celery] Error in connection parsing task: %s", str(e), exc_info=True
            )

            error_result = {
                "connections": [],
                "error": str(e),
                "timestamp": time.time(),
                "is_parsing": False,
            }

            # Update latest result
            self.latest_result = error_result

            # Write to IPC file
            self.write_to_ipc(error_result)
            return error_result

    def start_worker(self, script_path: Optional[str] = None) -> None:
        """
        Start the Celery worker and trigger initial connection parsing.

        Args:
            script_path (Optional[str]): Path to the script file
        """
        try:
            # Start worker
            worker = self.celery_app.Worker(
                concurrency=1,
                pool="solo",
                without_heartbeat=True,
                without_mingle=True,
                without_gossip=True,
            )

            # Run worker in a separate thread
            import threading

            worker_thread = threading.Thread(target=worker.start)
            worker_thread.daemon = True
            worker_thread.start()

            # If script path is provided, trigger initial parsing
            if script_path:
                logger.info(
                    "[Celery] Triggering initial connection parsing for script: %s",
                    script_path,
                )
                self.parse_connections.delay(script_path)

            logger.info("[Celery] Worker started successfully")

        except Exception as e:
            logger.error("[Celery] Error starting worker: %s", str(e))
            raise

    def stop_worker(self) -> None:
        """Stop the Celery worker and clean up."""
        try:
            # Stop all running tasks
            self.celery_app.control.purge()

            # Stop the worker
            self.celery_app.control.shutdown()

            # Remove IPC file and SQLite databases
            try:
                # Remove IPC file
                ipc_file = self.get_ipc_file()
                if os.path.exists(ipc_file):
                    os.remove(ipc_file)

                # Remove SQLite databases
                broker_db = os.path.join(self.temp_dir, "celery_broker.db")
                backend_db = os.path.join(self.temp_dir, "celery_backend.db")

                for db_file in [broker_db, backend_db]:
                    if os.path.exists(db_file):
                        os.remove(db_file)

            except Exception as e:
                logger.error("[Celery] Error removing temporary files: %s", str(e))

            logger.info("[Celery] Worker stopped successfully")

        except Exception as e:
            logger.error("[Celery] Error stopping worker: %s", str(e))
            raise

    def get_latest_result(self) -> Dict[str, Any]:
        """Get the latest connection parsing result."""
        return self.latest_result
