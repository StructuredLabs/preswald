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
        self._reactivity_enabled = True

        # Initialize session tracking
        self.script_runners: dict[str, ScriptRunner] = {}

        # Layout management
        self._layout_manager = LayoutManager()

    @contextmanager
    def active_atom(self, atom_name: str):
        """
        Context manager to track the currently executing atom during script execution.

        This is used by the reactive runtime to associate component accesses or side effects
        with the atom currently being evaluated. It enables dynamic dependency tracking
        by letting systems like the DAG or component registry know which atom is "active"
        when a component or value is used.

        Args:
            atom_name (str): The name of the atom that is being executed.
        """

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

    @property
    def is_reactivity_enabled(self):
        return self._reactivity_enabled

    def _ensure_dummy_atom(self, atom_name: str):
        """
        Register a placeholder (dummy) atom if one does not already exist.

        This is a fallback mechanism used during reactive execution when a component
        is referenced but no atom has been registered as its producer. While many
        components are produced inside reactive atoms (functions decorated with
        @workflow.atom), it's also valid for components to exist at the top level
        of a script, such components do not require producers.

        However, during reruns or DAG updates, we may attempt to associate a component
        with an atom. If no producer is found and a dependency edge is needed,
        we register a no-op dummy atom to preserve DAG consistency.

        This avoids runtime errors during reactivity while ensuring components and
        their relationships can be traced. If the atom is currently executing,
        dummy registration is skipped to avoid creating a self-loop in the DAG.
        """

        current_atom = self._workflow._current_atom
        if atom_name == current_atom:
            logger.info(f"[DAG] Skipping dummy registration for {atom_name=} (would self-loop)")
            return

        if atom_name not in self._workflow.atoms:
            logger.warning(
                "[DAG] No producer found; registering dummy atom (expected for standalone components, but may indicate a missing producer if dynamic inputs were intended) {atom_name=}"
            )

            dummy_func = lambda **kwargs: None
            self._workflow.atoms[atom_name] = Atom(
                name=atom_name,
                func=dummy_func,
                original_func=dummy_func,
            )

    def append_component(self, component):
        """
        Append a new or updated component to the active layout.

        This method plays a key role in the reactive runtime by determining whether
        a component has meaningfully changed and should be re-rendered. It ensures:

        - Components are validated for structure and type.
        - Redundant re-renders are avoided via intelligent patching.
        - Cleaned, normalized data (e.g., no NaNs) is sent to the frontend.
        - Dynamic layout updates are handled efficiently.

        Components may originate from user code, reactive atoms, or system-level updates.

        Args:
            component (dict or ComponentReturn):
                The component to append. Can be either a raw dictionary following the
                component protocol or a wrapped `ComponentReturn` object.
        """
        try:
            # TODO: Investigate stricter type checking for component unwrapping.
            # We currently unwrap any object with a `_preswald_component` attribute,
            # not just true `ComponentReturn` instances. Tightening this later will require
            # ensuring all component generators consistently return ComponentReturn objects.

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
            logger.info(f"[APPEND] Appending component {component_id=} {component_type=}")

            cleaned_component = clean_nan_values(component)

            if "id" in cleaned_component:
                # Attempt to patch; if no match, add it
                if not self._layout_manager.patch_component(cleaned_component):
                    self._layout_manager.add_component(cleaned_component)
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[APPEND] Added component with state {cleaned_component=}")
            else:
                self._layout_manager.add_component(cleaned_component)
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[APPEND] Added component without ID {cleaned_component=}")

        except Exception as e:
            logger.error(f"[APPEND] Error adding component: {e}", exc_info=True)

    def clear_components(self):
        """
        Clear all rendered components from the layout manager.

        This removes all visual components from the layout without modifying the underlying workflow DAG.
        Typically used when resetting the UI, reloading scripts, or handling client disconnects.
        """
        logger.info("[LAYOUT] Clearing all components from layout manager")
        self._layout_manager.clear_layout()

    def disable_reactivity(self):
        self._reactivity_enabled = False
        logger.info("[SERVICE] Reactivity disabled for fallback execution")

    def enable_reactivity(self):
        self._reactivity_enabled = True
        logger.info("[SERVICE] Reactivity re-enabled")

    def force_recompute(self, atom_names: set[str]) -> None:
        """
        Force specific atoms to recompute, regardless of input changes.

        Args:
            atom_names (set[str]): Set of atom names to force recompute.
        """
        logger.info(f"[DAG] Forcing recompute for atoms {atom_names=}")
        for atom_name in atom_names:
            atom = self._workflow.atoms.get(atom_name)
            if atom:
                atom.force_recompute = True
                logger.info(f"[DAG] Force recompute set for {atom_name=}")
            else:
                logger.warning(f"[DAG] No atom found with name {atom_name=}, skipping")

    def get_affected_components(self, changed_components: set[str]) -> set[str]:
        """
        Determine all components affected by a change in given components.

        This computes the transitive closure of dependencies: starting from the changed components,
        it identifies all downstream atoms whose outputs may need to be updated.

        Args:
            changed_components (set[str]): Set of changed component IDs.

        Returns:
            set[str]: Set of atom names that are affected.
        """
        affected_atoms = self._workflow._get_affected_atoms(changed_components)
        logger.info(f"[DAG] Dependency traversal complete {changed_components=} {affected_atoms=}")
        return affected_atoms

    def get_component_state(self, component_id: str, default: Any = None) -> Any:
        """
        Retrieve the current value of a component by ID.

        If a workflow atom is currently active, registers a dynamic dependency
        between the active atom and the component's producer atom. If no producer
        exists, a dummy atom is automatically registered to maintain DAG integrity.

        Args:
            component_id (str): The ID of the component to retrieve.
            default (Any): The value to return if the component ID is not found.

        Returns:
            Any: The current value associated with the component ID.
        """
        with self._lock:
            value = self._component_states.get(component_id, default)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"[STATE] Retrieved component state {component_id=} {value=}")
            else:
                logger.info(f"[STATE] Retrieved component state {component_id=}")

            # Handle unexpected wrapped ComponentReturn objects
            if isinstance(value, ComponentReturn):
                logger.warning(f"[STATE] Unwrapping unexpected ComponentReturn {component_id=}")
                value = value.value

            # Register DAG dependency if inside an active atom context
            producer = None
            if self._current_atom:
                producer = self._workflow.get_component_producer(component_id)

            if producer is None:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[DAG] No producer registered; registering dummy {component_id=} {self._current_atom=}")
                self._ensure_dummy_atom(self._current_atom)
            elif producer != self._current_atom:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[DAG] Registering dynamic dependency {self._current_atom=} {producer=}")
                self._workflow.atoms[self._current_atom].dependencies.add(producer)
            else:
                logger.info(f"[DAG] Producer matches current atom; skipping dependency {self._current_atom=} {component_id=}")

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
                    logger.info(f"[STATE] State changed for {component_id=}")
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[STATE]  - {cleaned_old_value=}\n  - {cleaned_new_value=}")
