import asyncio
import logging
import os
import threading
import time
from typing import Any, Callable, Dict, Optional

from fastapi import WebSocket, WebSocketDisconnect

from .managers.data import DataManager
from .managers.layout import LayoutManager
from .runner import ScriptRunner
from .utils import clean_nan_values, compress_data, optimize_plotly_data


logger = logging.getLogger(__name__)


class ServerPreswaldService:
    """
    Main service class that orchestrates the application components.
    Acts as a facade to provide a simplified interface to the complex subsystem.
    """

    _instance = None

    @classmethod
    def initialize(cls, script_path=None):
        if cls._instance is None:
            cls._instance = cls()
            if script_path:
                cls._instance._script_path = script_path
                cls._instance._initialize_data_manager(script_path)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError(
                "ServerPreswaldService not initialized. Did you call start_server()?"
            )
        return cls._instance

    def __init__(self):
        # Component state management
        self._component_states: Dict[str, Any] = {}
        self._lock = threading.Lock()

        # TODO: deprecated
        # Connection management
        self._connections: Dict[str, Any] = {}

        # Data management
        self.data_manager: DataManager = None  # set during server creation

        # Layout management
        self._layout_manager = LayoutManager()

        # Branding management
        self.branding_manager = None  # set during server creation

        # Initialize session tracking
        self.websocket_connections: Dict[str, WebSocket] = {}
        self.script_runners: Dict[str, ScriptRunner] = {}

        # Initialize service state
        self._script_path: Optional[str] = None
        self._is_shutting_down: bool = False

    @property
    def script_path(self) -> Optional[str]:
        return self._script_path

    @script_path.setter
    def script_path(self, path: str):
        """Set script path and initialize necessary components"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Script not found: {path}")

        self._script_path = path
        self._initialize_data_manager(path)

    async def register_client(
        self, client_id: str, websocket: WebSocket
    ) -> ScriptRunner:
        """Register a new client connection and create its script runner"""
        try:
            logger.info(f"[WebSocket] New connection request from client: {client_id}")
            await websocket.accept()
            logger.info(f"[WebSocket] Connection accepted for client: {client_id}")

            self.websocket_connections[client_id] = websocket

            # Create script runner for this client
            runner = ScriptRunner(
                session_id=client_id,
                send_message_callback=self._create_send_callback(websocket),
                initial_states=self._component_states,
            )
            self.script_runners[client_id] = runner

            # Send initial states
            await self._send_initial_states(websocket)

            # Start script if path is set
            if self._script_path:
                await runner.start(self._script_path)

            return runner

        except WebSocketDisconnect:
            logger.info(f"[WebSocket] Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error registering client {client_id}: {e}")
            raise

    async def unregister_client(self, client_id: str):
        """Clean up resources for a disconnected client"""
        try:
            # Clean up websocket
            if websocket := self.websocket_connections.pop(client_id, None):
                try:
                    # Check if websocket is not already closed
                    if not websocket.client_state.DISCONNECTED:
                        await websocket.close(code=1000, reason="Server shutting down")
                except Exception as e:
                    # Log but don't raise if websocket is already closed
                    logger.debug(
                        f"Websocket already closed for client {client_id}: {e}"
                    )

            self._layout_manager.clear_layout()

            # Clean up script runner
            if runner := self.script_runners.pop(client_id, None):
                await runner.stop()

            asyncio.create_task(self._broadcast_connections())  # noqa: RUF006
        except Exception as e:
            logger.error(f"Error unregistering client {client_id}: {e}")

    async def handle_client_message(self, client_id: str, message: Dict[str, Any]):
        """Process incoming messages from clients"""
        start_time = time.time()
        try:
            msg_type = message.get("type")

            if msg_type == "component_update":
                await self._handle_component_update(client_id, message)
            else:
                logger.warning(f"Unknown message type: {msg_type}")

        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
            await self._send_error(client_id, str(e))
        finally:
            logger.info(
                f"[WebSocket] Total message handling took {time.time() - start_time:.3f}s"
            )

    async def shutdown(self):
        """Gracefully shut down the service"""
        self._is_shutting_down = True
        logger.info("Received shutdown signal, cleaning up...")

        # Clean up all client connections
        for client_id in list(self.websocket_connections.keys()):
            await self.unregister_client(client_id)

    def append_component(self, component):
        """Add a component to the layout manager"""
        try:
            if isinstance(component, dict):
                # Clean any NaN values in the component
                clean_start = time.time()
                cleaned_component = clean_nan_values(component)
                logger.debug(
                    f"[RENDER] NaN cleanup took {time.time() - clean_start:.3f}s"
                )

                # Ensure component has current state
                if "id" in cleaned_component:
                    component_id = cleaned_component["id"]
                    if component_id not in self._layout_manager.seen_ids:
                        # Update component with current state if it exists
                        if "value" in cleaned_component:
                            current_state = self.get_component_state(component_id)
                            if current_state is not None:
                                cleaned_component["value"] = clean_nan_values(
                                    current_state
                                )
                                logger.debug(
                                    f"Updated component {component_id} with state: {current_state}"
                                )
                        self._layout_manager.add_component(cleaned_component)
                        logger.debug(f"Added component with state: {cleaned_component}")
                else:
                    # Components without IDs are added as-is
                    self._layout_manager.add_component(cleaned_component)
                    logger.debug(f"Added component without ID: {cleaned_component}")
            else:
                # Convert HTML string to component data
                component = {
                    "type": "html",
                    "content": str(component),
                    "size": 1.0,  # HTML components take full width
                }
                self._layout_manager.add_component(component)
                logger.debug(f"Added HTML component: {component}")
        except Exception as e:
            logger.error(f"Error adding component: {e}", exc_info=True)

    def get_rendered_components(self):
        rows = self._layout_manager.get_layout()
        return {"rows": rows}

    def get_component_state(self, component_id: str, default: Any = None) -> Any:
        """Get the current state of a component"""
        with self._lock:
            value = self._component_states.get(component_id, default)
            logger.debug(f"[STATE] Getting state for {component_id}: {value}")
            return value

    def _update_component_states(self, states: Dict[str, Any]):
        """Update the state of a component and trigger callbacks"""
        with self._lock:
            logger.debug("[STATE] Updating states")
            for component_id, new_value in states.items():
                old_value = self._component_states.get(component_id)

                # Clean NaN values before comparison and storage
                cleaned_new_value = clean_nan_values(new_value)
                cleaned_old_value = clean_nan_values(old_value)

                if cleaned_old_value != cleaned_new_value:
                    self._component_states[component_id] = cleaned_new_value

                    # Log state change
                    logger.debug(f"[STATE] State changed for {component_id}:")
                    logger.debug(f"  - Old value: {cleaned_old_value}")
                    logger.debug(f"  - New value: {cleaned_new_value}")

    def _create_send_callback(self, websocket: WebSocket) -> Callable:
        """Create a message sending callback for a specific websocket"""

        async def send_message(msg: Dict[str, Any]):
            if not self._is_shutting_down:
                try:
                    await websocket.send_json(msg)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")

        return send_message

    async def _send_initial_states(self, websocket: WebSocket):
        """Send initial component states to a new client"""
        try:
            with self._lock:
                initial_states = dict(self._component_states)
            await websocket.send_json(
                {"type": "initial_state", "states": initial_states}
            )
        except Exception as e:
            logger.error(f"Error sending initial states: {e}")

    async def _handle_component_update(self, client_id: str, message: Dict[str, Any]):
        """Handle component state update messages"""
        states = message.get("states", {})
        if not states:
            await self._send_error(client_id, "Component update missing states")
            raise ValueError("Component update missing states")

        # Only rerun if any state actually changed
        changed_states = {
            k: v for k, v in states.items()
            if clean_nan_values(self.get_component_state(k)) != clean_nan_values(v)
        }

        if not changed_states:
            logger.debug(f"[STATE] No actual state changes detected. Skipping rerun.")
            return

        # Update only changed states
        self._update_component_states(changed_states)
        self._layout_manager.clear_layout()

        # Update states and trigger script rerun
        runner = self.script_runners.get(client_id)
        if runner:
            await runner.rerun(changed_states)

        # Broadcast updates to other clients
        await self._broadcast_state_updates(changed_states, exclude_client=client_id)

    async def _broadcast_state_updates(
        self, states: Dict[str, Any], exclude_client: Optional[str] = None
    ):
        """Broadcast state updates to all clients except the sender"""

        for component_id, value in states.items():
            if isinstance(value, dict) and "data" in value and "layout" in value:
                value = optimize_plotly_data(value)

            # Compress the data
            compressed_value = compress_data(value)

            message = {
                "type": "state_update",
                "component_id": component_id,
                "value": compressed_value,
                "compressed": True,
            }

            for client_id, websocket in self.websocket_connections.items():
                if client_id != exclude_client:
                    try:
                        await websocket.send_bytes(compress_data(message))
                    except Exception as e:
                        logger.error(f"Error broadcasting to {client_id}: {e}")

    async def _broadcast_connections(self):
        """Broadcast current connections to all clients"""
        try:
            connection_list = []
            # Use websocket_connections instead of deprecated connection_manager
            for client_id, websocket in self.websocket_connections.items():  # noqa: B007
                connection_info = {
                    "name": client_id,
                    "type": "WebSocket",
                    "details": f"Active WebSocket connection for client {client_id}",
                }
                connection_list.append(connection_info)

            # Broadcast to all connected clients
            for websocket in self.websocket_connections.values():
                try:
                    await websocket.send_json(
                        {"type": "connections_update", "connections": connection_list}
                    )
                except Exception as e:
                    logger.debug(f"Error sending connection update to client: {e}")

        except Exception as e:
            logger.error(f"Error broadcasting connections: {e}")
            # Don't raise the exception to prevent disrupting the main flow

    async def _send_error(self, client_id: str, message: str):
        """Send error message to a specific client"""
        if websocket := self.websocket_connections.get(client_id):
            try:
                await websocket.send_json(
                    {"type": "error", "content": {"message": message}}
                )
            except Exception as e:
                logger.error(f"Error sending error message: {e}")

    def clear_components(self):
        """Clear all components from the layout manager"""
        self._layout_manager.clear_layout()

    def _initialize_data_manager(self, script_path: str) -> None:
        script_dir = os.path.dirname(script_path)
        preswald_path = os.path.join(script_dir, "preswald.toml")
        secrets_path = os.path.join(script_dir, "secrets.toml")

        self.data_manager = DataManager(
            preswald_path=preswald_path, secrets_path=secrets_path
        )
