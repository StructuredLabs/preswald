import logging
import os
import time
from threading import Lock
from typing import Any, Callable, Dict, Optional

from preswald.engine.runner import ScriptRunner
from preswald.engine.utils import (
    RenderBuffer,
    clean_nan_values,
    compress_data,
    optimize_plotly_data,
)

from .managers.data import DataManager
from .managers.layout import LayoutManager


logger = logging.getLogger(__name__)


class BasePreswaldService:
    """
    Abstract base class for shared PreswaldService logic.
    Manages component states, diffing, and render buffer.
    """

    _not_initialized_msg = "Base service not initialized."

    def __init__(self):
        self._component_states: Dict[str, Any] = {}
        self._lock = Lock()

        # Data management
        self.data_manager: Optional[DataManager] = None  # set during server creation

        # Initialize service state
        self._script_path: Optional[str] = None
        self._is_shutting_down: bool = False
        self._render_buffer = RenderBuffer()

        # Initialize session tracking
        self.script_runners: Dict[str, ScriptRunner] = {}

        # Layout management
        self._layout_manager = LayoutManager()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError(cls._not_initialized_msg)
        return cls._instance

    @classmethod
    def initialize(cls, script_path=None):
        if cls._instance is None:
            cls._instance = cls()
            if script_path:
                cls._instance._script_path = script_path
                cls._instance._initialize_data_manager(script_path)
        return cls._instance

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

    def append_component(self, component):
        """Add a component to the layout manager"""
        try:

            if isinstance(component, dict):
                logger.info(f"[APPEND] Appending component: {component.get('id')}, type: {component.get('type')}")
                # Clean any NaN values in the component
                clean_start = time.time()
                cleaned_component = clean_nan_values(component)
                logger.debug(f"NaN cleanup took {time.time() - clean_start:.3f}s")

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
                                if logger.isEnabledFor(logging.DEBUG):
                                    logger.debug(
                                        f"Updated component {component_id} with state: {current_state}"
                                    )
                        self._layout_manager.add_component(cleaned_component)
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"Added component with state: {cleaned_component}")
                else:
                    # Components without IDs are added as-is
                    self._layout_manager.add_component(cleaned_component)
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"Added component without ID: {cleaned_component}")
            else:
                # Convert HTML string to component data
                component = {
                    "type": "html",
                    "content": str(component),
                    "size": 1.0,  # HTML components take full width
                }
                self._layout_manager.add_component(component)
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Added HTML component: {component}")
        except Exception as e:
            logger.error(f"Error adding component: {e}", exc_info=True)

    def clear_components(self):
        """Clear all components from the layout manager"""
        self._layout_manager.clear_layout()

    def get_component_state(self, component_id: str, default: Any = None) -> Any:
        """Retrieve the current state for a given component."""
        with self._lock:
            value = self._component_states.get(component_id, default)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"[STATE] Getting state for {component_id}: {value}")
            return value

    def get_rendered_components(self):
        """Get all rendered components"""
        rows = self._layout_manager.get_layout()
        return {"rows": rows}

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

    def should_render(self, component_id: str, new_value: Any) -> bool:
        """Determine if a component should re-render based on its new value."""
        return self._render_buffer.should_render(component_id, new_value)

    async def shutdown(self):
        """Shut down the service"""
        self._is_shutting_down = True
        logger.info("Shutting down service...")

        # Clean up all client connections
        for client_id in list(self.websocket_connections.keys()):
            await self.unregister_client(client_id)

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

        except Exception as e:
            logger.error(f"Error unregistering client {client_id}: {e}")

    def _create_send_callback(self, websocket: Any) -> Callable:
        """Create a message sending callback for a specific websocket"""

        async def send_message(msg: Dict[str, Any]):
            if not self._is_shutting_down:
                try:
                    await websocket.send_json(msg)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")

        return send_message

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

    async def _handle_component_update(self, client_id: str, message: Dict[str, Any]):
        """Handle component state update messages"""
        states = message.get("states", {})
        if not states:
            await self._send_error(client_id, "Component update missing states")
            raise ValueError("Component update missing states")

        # Only rerun if any state actually changed
        changed_states = {
            k: v for k, v in states.items()
            if self.should_render(k, v)
        }

        if not changed_states:
            logger.debug("[STATE] No actual state changes detected. Skipping rerun.")
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

    def _initialize_data_manager(self, script_path: str) -> None:
        script_dir = os.path.dirname(script_path)
        preswald_path = os.path.join(script_dir, "preswald.toml")
        secrets_path = os.path.join(script_dir, "secrets.toml")

        self.data_manager = DataManager(
            preswald_path=preswald_path, secrets_path=secrets_path
        )

    async def _register_common_client_setup(self, client_id: str, websocket: Any) -> ScriptRunner:
        logger.info(f"Registering client: {client_id}")

        self.websocket_connections[client_id] = websocket

        runner = ScriptRunner(
            session_id=client_id,
            send_message_callback=self._create_send_callback(websocket),
            initial_states=self._component_states,
        )
        self.script_runners[client_id] = runner

        await self._send_initial_states(websocket)

        if self._script_path:
            await runner.start(self._script_path)

        return runner

    async def _send_error(self, client_id: str, message: str):
        """Send error message to a client"""
        if websocket := self.websocket_connections.get(client_id):
            try:
                await websocket.send_json(
                    {"type": "error", "content": {"message": message}}
                )
            except Exception as e:
                logger.error(f"Error sending error message: {e}")

    async def _send_initial_states(self, websocket: Any):
        """Send initial component states to a new client"""
        try:
            with self._lock:
                initial_states = dict(self._component_states)
            await websocket.send_json(
                {"type": "initial_state", "states": initial_states}
            )
        except Exception as e:
            logger.error(f"Error sending initial states: {e}")

    def _update_component_states(self, states: Dict[str, Any]):
        """Update internal state dictionary with cleaned component values."""
        with self._lock:
            logger.debug("[STATE] Updating states")
            for component_id, new_value in states.items():
                old_value = self._component_states.get(component_id)

                cleaned_new_value = clean_nan_values(new_value)
                cleaned_old_value = clean_nan_values(old_value)

                if cleaned_old_value != cleaned_new_value:
                    self._component_states[component_id] = cleaned_new_value
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[STATE] State changed for {component_id}:")
                        logger.debug(f"  - Old value: {cleaned_old_value}")
                        logger.debug(f"  - New value: {cleaned_new_value}")
