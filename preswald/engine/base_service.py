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

    def append_component(self, component):
        """Add a component to the layout manager"""
        try:
            if isinstance(component, dict):
                logger.info(
                    f"[APPEND] Appending component: {component.get('id')}, type: {component.get('type')}"
                )
                # Clean any NaN values in the component
                clean_start = time.time()
                cleaned_component = clean_nan_values(component)
                logger.debug(f"NaN cleanup took {time.time() - clean_start:.3f}s")

                # Ensure component has current state
                if "id" in cleaned_component:
                    component_id = cleaned_component["id"]
                    logger.info(f"[TEST] append_component() called with id: {component_id}")
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
                        with self.active_atom(self._workflow._current_atom):
                            # Track the producing atom
                            logger.info(f"[DEBUG] Current atom before register: {self._workflow._current_atom}")
                            self._workflow.register_component_producer(component_id)

                            # Store return value in workflow context (if present)
                            if "value" in cleaned_component:
                                producer = self._workflow.get_component_producer(component_id)
                                if producer:
                                    self._workflow.context.set_variable(producer, cleaned_component["value"])
                                    logger.info(f"[DAG] Stored return value of {component_id} in context under {producer}")

                            # Register dummy atom if needed
                            if component_id not in self._workflow.atoms:
                                # TODO: TEMP fallback - clean up after final DAG model is enforced
                                # This is a fallback for cases where atoms are referenced before being explicitly defined.
                                # This should only happen in testing or non-standard usage (e.g., manual workflow.execute()).
                                # In the final model, atoms should always be registered via the @atom decorator.
                                logger.warning(
                                    f"[DAG] (append_component) Atom '{component_id}' was used as a dependency before being explicitly defined. "
                                    "Registering placeholder (dummy) atom."
                                )
                                self._register_dummy_atom(component_id)

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

    def force_recompute(self, component_ids: set[str]) -> None:
        """Mark components as needing recomputation."""
        logger.debug(f"[DAG] Forcing recompute for: {component_ids}")
        for cid in component_ids:
            if cid in self._workflow.atoms:
                self._workflow.atoms[cid].force_recompute = True

    def get_affected_components(self, changed_components: set[str]) -> set[str]:
        """Compute all components affected by the updated component state."""
        affected = self._workflow._get_affected_atoms(changed_components)
        logger.debug(f"Changed: {changed_components} → Affected: {affected}")
        return affected

    def get_component_state(self, component_id: str, default: Any = None) -> Any:
        """Retrieve the current state for a given component."""
        with self._lock:
            value = self._component_states.get(component_id, default)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"[STATE] Getting state for {component_id}: {value}")

            # register a DAG dependency if workflow is active
            if self._current_atom:
                # track component-level dependency
                logger.debug(f"[DAG] {self._current_atom} depends on {component_id}")
                if self._current_atom not in self._workflow.atoms:
                    # TODO: TEMP fallback - clean up after final DAG model is enforced
                    # This is a fallback for cases where atoms are referenced before being explicitly defined.
                    # This should only happen in testing or non-standard usage (e.g., manual workflow.execute()).
                    # In the final model, atoms should always be registered via the @atom decorator.
                    logger.warning(
                        f"[DAG] (get_component_state) Atom '{self._current_atom}' was used as a dependency before being explicitly defined. "
                        "Registering placeholder (dummy) atom."
                    )
                    self._register_dummy_atom(self._current_atom)
                if component_id != self._current_atom:
                    self._workflow.atoms[self._current_atom].dependencies.add(component_id)

                # also register dependency on the atom that produced this component, if known
                producer = self._workflow.get_component_producer(component_id)
                if producer:
                    logger.debug(f"[DAG] {self._current_atom} also depends on producer atom {producer}")
                    self._workflow.atoms[self._current_atom].dependencies.add(producer)

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
        # TODO: TEMP fallback - clean up after final DAG model is enforced
        logger.warning(f"[DAG] (fallback) Registering dummy atom for '{atom_name}'")
        dummy_func = lambda **kwargs: None
        self.atoms[atom_name] = Atom(name=atom_name, func=dummy_func, original_func=dummy_func)

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
