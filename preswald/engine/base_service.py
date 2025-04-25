import logging
import os
import time
from collections.abc import Callable
from threading import Lock
from typing import Any, Callable, Dict, Optional
from contextlib import contextmanager

from preswald.engine.runner import ScriptRunner
from preswald.engine.utils import (
    RenderBuffer,
    clean_nan_values,
    compress_data,
    optimize_plotly_data,
)
from preswald.interfaces.workflow import Workflow, Atom
from preswald.interfaces.component_return import ComponentReturn
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
        self._component_states: dict[str, Any] = {}
        self._lock = Lock()

        # Data management
        self.data_manager: DataManager | None = None  # set during server creation

        # Initialize service state
        self._script_path: str | None = None
        self._is_shutting_down: bool = False
        self._render_buffer = RenderBuffer()

        # DAG workflow engine
        self._workflow = Workflow(service=self)
        self._current_atom: Optional[str] = None

        # Initialize session tracking
        self.script_runners: dict[str, ScriptRunner] = {}

        # Layout management
        self._layout_manager = LayoutManager()

    @contextmanager
    def active_atom(self, atom_name: str):
        previous_atom = self._current_atom
        self._current_atom = atom_name
        try:
            yield
        finally:
            self._current_atom = previous_atom

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
    def script_path(self) -> str | None:
        return self._script_path

    @script_path.setter
    def script_path(self, path: str):
        """Set script path and initialize necessary components"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Script not found: {path}")

        self._script_path = path
        self._initialize_data_manager(path)

    def _ensure_dummy_atom(self, atom_name: str):
        """Helper to ensure a dummy atom is registered if it doesn’t already exist and isn’t the current atom."""
        current_atom = self._workflow._current_atom
        if atom_name == current_atom:
            #logger.debug(f"[DAG] Skipping dummy registration for {atom_name} (would self-loop)")
            logger.info(f"[DAG] Skipping dummy registration for {atom_name} (would self-loop)")
            return

        if atom_name not in self._workflow.atoms:
            logger.warning(f"[DAG] (fallback) Registering dummy atom for '{atom_name}'")
            dummy_func = lambda **kwargs: None
            self._workflow.atoms[atom_name] = Atom(
                name=atom_name,
                func=dummy_func,
                original_func=dummy_func,
            )

    def append_component(self, component):
        """
        Append a component to the current layout if it is valid and not a duplicate.

        This method performs the following steps:
        - Unwraps the component if it is a ComponentReturn wrapper.
        - Validates that the component is a dictionary with a valid "type".
        - Cleans the component by removing or replacing NaN values.
        - Uses the layout manager to patch an existing component or add a new one.

        Logs are emitted at various levels for debugging and tracing component flow.

        Args:
            component (dict or ComponentReturn): The component to append. Can be a raw dict or a wrapped object.

        Returns:
            None
        """
        try:
            # Unwrap if necessary
            if hasattr(component, "_preswald_component"):
                component = component._preswald_component

            if not isinstance(component, dict):
                logger.warning(f"[APPEND] Skipping non-dict component: {component}")
                return

            if "type" not in component or not isinstance(component["type"], str):
                logger.warning(f"[APPEND] Skipping component with no valid type: {component}")
                return

            component_id = component.get("id")
            component_type = component.get("type")
            logger.info(f"[APPEND] Appending component: {component_id}, type: {component_type}")

            cleaned_component = clean_nan_values(component)

            if "id" in cleaned_component:
                # Attempt to patch; if no match, add it
                if not self._layout_manager.patch_component(cleaned_component):
                    self._layout_manager.add_component(cleaned_component)
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[APPEND] Added component with state: {cleaned_component}")
            else:
                self._layout_manager.add_component(cleaned_component)
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[APPEND] Added component without ID: {cleaned_component}")

        except Exception as e:
            logger.error(f"[APPEND] Error adding component: {e}", exc_info=True)

    def clear_components(self):
        """Clear all components from the layout manager"""
        self._layout_manager.clear_layout()

    def force_recompute(self, component_ids: set[str]) -> None:
        """Mark components as needing recomputation."""
        logger.info(f"[DAG] Forcing recompute for: {component_ids}")
        for cid in component_ids:
            if cid in self._workflow.atoms:
                self._workflow.atoms[cid].force_recompute = True

    def get_affected_components(self, changed_components: set[str]) -> set[str]:
        """Compute all components affected by the updated component state."""
        affected = self._workflow._get_affected_atoms(changed_components)
        logger.info(f"Changed: {changed_components} → Affected: {affected}")
        return affected

    def get_component_state(self, component_id: str, default: Any = None) -> Any:
        with self._lock:
            value = self._component_states.get(component_id, default)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"[STATE] Getting state for {component_id}: {value}")
            logger.info(f"[STATE] Getting state for {component_id}: {value}")

            if isinstance(value, ComponentReturn):
                logger.warning(f"[STATE] Got unexpected ComponentReturn in state for {component_id}")
                value = value.value  # unwrap

            if self._current_atom:
                producer = self._workflow.get_component_producer(component_id)

                # ⛔ Don't create circular edge: current_atom → its own output
                if component_id != self._current_atom and producer != self._current_atom:
                    #logger.info(f"[DAG] {self._current_atom} depends on {component_id}")
                    #self._workflow.atoms[self._current_atom].dependencies.add(component_id)

                    if producer:
                        logger.info(f"[DAG] {self._current_atom} also depends on producer atom {producer}")
                        self._workflow.atoms[self._current_atom].dependencies.add(producer)

                    # Register fallback only if atom not declared
                    self._ensure_dummy_atom(self._current_atom)

            return value

    def get_rendered_components(self):
        """Get all rendered components"""
        rows = self._layout_manager.get_layout()
        return {"rows": rows}

    def get_workflow(self) -> Workflow:
        return self._workflow

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

        async def send_message(msg: dict[str, Any]):
            if not self._is_shutting_down:
                try:
                    await websocket.send_json(msg)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")

        return send_message

    async def _broadcast_state_updates(
        self, states: dict[str, Any], exclude_client: str | None = None
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

    async def _handle_component_update(self, client_id: str, message: dict[str, Any]):
        """Handle component state update messages"""
        states = message.get("states", {})
        if not states:
            await self._send_error(client_id, "Component update missing states")
            raise ValueError("Component update missing states")

        # Only rerun if any state actually changed
        changed_states = {k: v for k, v in states.items() if self.should_render(k, v)}

        if not changed_states:
            logger.info("[STATE] No actual state changes detected. Skipping rerun.")
            return

        # Update only changed states
        self._update_component_states(changed_states)

        # Update states and trigger script rerun
        runner = self.script_runners.get(client_id)
        if runner:
            await runner.rerun(changed_states)

        # Broadcast updates to other clients
        await self._broadcast_state_updates(changed_states, exclude_client=client_id)

    def connect_data_manager(self):
        """Connect the data manager"""
        self.data_manager.connect()

    def _initialize_data_manager(self, script_path: str) -> None:
        script_dir = os.path.dirname(script_path)
        preswald_path = os.path.join(script_dir, "preswald.toml")
        secrets_path = os.path.join(script_dir, "secrets.toml")

        self.data_manager = DataManager(
            preswald_path=preswald_path, secrets_path=secrets_path
        )

    async def _register_common_client_setup(
        self, client_id: str, websocket: Any
    ) -> ScriptRunner:
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

    def _register_dummy_atom(self, atom_name: str):
        """Safely register a placeholder atom to avoid undefined references."""
        current_atom = self._workflow._current_atom

        # Avoid registering a dummy that would point to itself
        if atom_name == current_atom:
            logger.info(f"[DAG] Skipping dummy registration for {atom_name} (would self-loop)")
            return

        if atom_name not in self._workflow.atoms:
            logger.warning(f"[DAG] (fallback) Registering dummy atom for '{atom_name}'")
            dummy_func = lambda **kwargs: None
            self._workflow.atoms[atom_name] = Atom(
                name=atom_name,
                func=dummy_func,
                original_func=dummy_func,
            )

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

    def _update_component_states(self, states: dict[str, Any]):
        """Update internal state dictionary with cleaned component values."""
        with self._lock:
            logger.info("[STATE] Updating states")
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
                    logger.info(f"[STATE] State changed for {component_id}:")
                    logger.info(f"  - Old value: {cleaned_old_value}")
                    logger.info(f"  - New value: {cleaned_new_value}")
