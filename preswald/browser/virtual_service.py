"""
Browser compatibility layer for Preswald in Pyodide environments
"""

import asyncio
import logging
import sys
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)

# Detect if running in Pyodide
IS_PYODIDE = "pyodide" in sys.modules

if IS_PYODIDE:
    from js import console, window  # type: ignore


class VirtualWebSocket:
    """
    Simulates WebSocket functionality in browser environment.
    Acts as a compatibility layer between Pyodide and JavaScript.
    """

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.is_connected = True
        self.client_state = type("ClientState", (), {"DISCONNECTED": False})

        # Detect if running in browser mode (iframe in Runewald) or server mode
        self.is_browser_mode = IS_PYODIDE and getattr(
            window, "__PRESWALD_BROWSER_MODE", False
        )
        console.log(f"[Communication] is browser mode: {self.is_browser_mode}")

    async def send_json(self, data: Dict[str, Any]):
        """Send JSON data to JavaScript frontend"""
        if not self.is_connected:
            logger.error(f"Cannot send message, connection closed for {self.client_id}")
            return

        if IS_PYODIDE:
            try:
                import json

                json_str = json.dumps(data)
                # Convert Python dict to JavaScript object
                if self.is_browser_mode:
                    from js import JSON

                    js_data = JSON.parse(json_str)
                    # js_data = to_js(data, dict_converter=Object.fromEntries)
                    window.parent.postMessage(js_data, "*")
                    console.log(f"[Python] Sent postMessage: {data}")
                else:
                    try:
                        from js import JSON, handlePythonMessage  # type: ignore

                        js_data = JSON.parse(json_str)

                        handlePythonMessage(self.client_id, js_data)
                        console.log(f"[Python] Sent to handlePythonMessage: {data}")
                    except ImportError:
                        from js import JSON

                        js_data = JSON.parse(json_str)
                        window.parent.postMessage(js_data, "*")
                        console.log(f"[Python] Sent postMessage: {data}")
            except Exception as e:
                logger.error(f"Error sending message to JS: {e}")

    async def send_bytes(self, data: bytes):
        """Send binary data to JavaScript frontend"""
        if not self.is_connected:
            logger.error(f"Cannot send bytes, connection closed for {self.client_id}")
            return

        if IS_PYODIDE:
            try:
                array = window.Uint8Array.new(len(data))
                if self.is_browser_mode:
                    # Use postMessage for binary data in browser mode
                    for i, b in enumerate(data):
                        array[i] = b
                    window.parent.postMessage(
                        {"type": "binary_message", "data": array}, "*"
                    )
                    console.log("[Python] Sent binary postMessage")
                else:
                    # Use handlePythonBinaryMessage for server/Pyodide mode (if needed)
                    try:
                        from js import handlePythonBinaryMessage  # type: ignore

                        for i, b in enumerate(data):
                            array[i] = b
                        handlePythonBinaryMessage(self.client_id, array)
                        console.log("[Python] Sent to handlePythonBinaryMessage")
                    except ImportError:
                        logger.warning(
                            "handlePythonBinaryMessage not available, using postMessage fallback"
                        )
                        array = window.Uint8Array.new(len(data))
                        for i, b in enumerate(data):
                            array[i] = b
                        window.parent.postMessage(
                            {"type": "binary_message", "data": array}, "*"
                        )
                        console.log("[Python] Sent binary postMessage fallback")
            except Exception as e:
                logger.error(f"Error sending binary message to JS: {e}")

    async def accept(self):
        """Accept the connection (no-op in virtual implementation)"""
        pass

    async def close(self, code=1000, reason="Connection closed"):
        """Close the connection"""
        self.is_connected = False
        self.client_state.DISCONNECTED = True


class VirtualPreswaldService:
    """
    Browser-compatible implementation of PreswaldService that works in Pyodide
    without requiring FastAPI, uvicorn, or websockets.
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
                "VirtualPreswaldService not initialized. Did you call initialize()?"
            )
        return cls._instance

    def __init__(self):
        """Initialize the service with browser-compatible components"""
        from threading import Lock

        # Core state management (similar to original)
        self._component_states = {}
        self._lock = Lock()
        self._is_shutting_down = False
        self._script_path = None

        # Create browser-compatible managers
        from preswald.engine.managers.layout import LayoutManager

        self._layout_manager = LayoutManager()

        # Client connections (virtual)
        self.websocket_connections = {}
        self.script_runners = {}

        # In browser, set dummy branding manager
        self.branding_manager = type(
            "DummyBrandingManager",
            (),
            {
                "static_dir": "",
                "get_branding_config": lambda *args: {
                    "name": "Preswald",
                    "favicon": "/favicon.ico",
                },
            },
        )()

        # Data manager will be set during initialization
        self.data_manager = None

        # Register with JavaScript
        self._register_js_handlers()

    def _register_js_handlers(self):
        """Register Python handlers with JavaScript"""
        if not IS_PYODIDE:
            return

        # Create proxies for JavaScript to call Python
        from pyodide.ffi import create_proxy  # type: ignore

        def handle_message_from_js(client_id, message_type, data):
            try:
                import json

                # Convert JsProxy to real Python dict using JSON workaround
                # Note: Although we're on Pyodide 0.27.2, the environment seems to lack `to_py`
                # likely due to an incomplete or custom Pyodide build

                json_str = window.JSON.stringify(data)
                py_data = json.loads(json_str)

                if isinstance(py_data, dict):
                    message = dict(py_data)
                    message["type"] = message_type
                else:
                    message = {"type": message_type, "data": py_data}

                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Handling JS message from {client_id}: {message}")

                asyncio.create_task(self.handle_client_message(client_id, message))   # noqa: RUF006
                return True
            except Exception:
                import traceback
                logger.error("Error in handle_message_from_js: %s", traceback.format_exc())
                return False

        # Export the function to JavaScript
        handle_message_proxy = create_proxy(handle_message_from_js)

        window.handleMessageFromJS = handle_message_proxy

        console.log("Registered Python message handlers with JavaScript")

    async def register_client(self, client_id: str, websocket=None):
        """Register a client with the service"""
        try:
            logger.info(f"Registering client: {client_id}")

            # In browser, create a virtual websocket if none provided
            if websocket is None:
                websocket = VirtualWebSocket(client_id)

            # Accept the connection
            await websocket.accept()

            # Store the connection
            self.websocket_connections[client_id] = websocket

            # Create a script runner
            from preswald.engine.runner import ScriptRunner

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

        except Exception as e:
            logger.error(f"Error registering client {client_id}: {e}")
            raise

    def _create_send_callback(self, websocket):
        """Create a callback to send messages to the client"""

        async def send_message(msg: Dict[str, Any]):
            if not self._is_shutting_down:
                try:
                    await websocket.send_json(msg)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")

        return send_message

    async def _send_initial_states(self, websocket):
        """Send initial component states to a client"""
        try:
            with self._lock:
                initial_states = dict(self._component_states)
            await websocket.send_json(
                {"type": "initial_state", "states": initial_states}
            )
        except Exception as e:
            logger.error(f"Error sending initial states: {e}")

    async def handle_client_message(self, client_id: str, message: Dict[str, Any]):
        """Process messages from clients"""
        import time

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
            logger.info(f"Total message handling took {time.time() - start_time:.3f}s")

    async def _handle_component_update(self, client_id: str, message: Dict[str, Any]):
        """Handle component state updates"""
        states = message.get("states", {})
        if not states:
            await self._send_error(client_id, "Component update missing states")
            raise ValueError("Component update missing states")

        # Only rerun if any state actually changed
        from preswald.engine.utils import clean_nan_values

        changed_states = {
            k: v for k, v in states.items()
            if clean_nan_values(self.get_component_state(k)) != clean_nan_values(v)
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

    def _update_component_states(self, states: Dict[str, Any]):
        """Update component states"""
        from preswald.engine.utils import clean_nan_values

        with self._lock:
            logger.debug("Updating states")
            for component_id, new_value in states.items():
                old_value = self._component_states.get(component_id)

                # Clean NaN values
                cleaned_new_value = clean_nan_values(new_value)
                cleaned_old_value = clean_nan_values(old_value)

                if cleaned_old_value != cleaned_new_value:
                    self._component_states[component_id] = cleaned_new_value

                    logger.debug(f"State changed for {component_id}:")
                    logger.debug(f"  - Old value: {cleaned_old_value}")
                    logger.debug(f"  - New value: {cleaned_new_value}")

    async def _broadcast_state_updates(
        self, states: Dict[str, Any], exclude_client: Optional[str] = None
    ):
        """Broadcast state updates to all clients except the sender"""
        from preswald.engine.utils import compress_data, optimize_plotly_data

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

    async def _send_error(self, client_id: str, message: str):
        """Send error message to a client"""
        if websocket := self.websocket_connections.get(client_id):
            try:
                await websocket.send_json(
                    {"type": "error", "content": {"message": message}}
                )
            except Exception as e:
                logger.error(f"Error sending error message: {e}")

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

    async def shutdown(self):
        """Shut down the service"""
        self._is_shutting_down = True
        logger.info("Shutting down service...")

        # Clean up all client connections
        for client_id in list(self.websocket_connections.keys()):
            await self.unregister_client(client_id)

    def _initialize_data_manager(self, script_path: str) -> None:
        """Initialize the data manager"""
        import os

        script_dir = os.path.dirname(script_path)
        preswald_path = os.path.join(script_dir, "preswald.toml")
        secrets_path = os.path.join(script_dir, "secrets.toml")

        from preswald.engine.managers.data import DataManager

        self.data_manager = DataManager(
            preswald_path=preswald_path, secrets_path=secrets_path
        )

    # Same methods as original to maintain compatibility
    @property
    def script_path(self) -> Optional[str]:
        return self._script_path

    @script_path.setter
    def script_path(self, path: str):
        """Set script path and initialize necessary components"""
        import os

        if not os.path.exists(path):
            raise FileNotFoundError(f"Script not found: {path}")

        self._script_path = path
        self._initialize_data_manager(path)

    def append_component(self, component):
        """Add a component to the layout manager"""
        try:
            from preswald.engine.utils import clean_nan_values

            if isinstance(component, dict):
                # Clean any NaN values in the component
                import time

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
            logger.error(f"Error adding component: {e}")

    def get_rendered_components(self):
        """Get all rendered components"""
        rows = self._layout_manager.get_layout()
        return {"rows": rows}

    def get_component_state(self, component_id: str, default: Any = None) -> Any:
        """Get the current state of a component"""
        with self._lock:
            value = self._component_states.get(component_id, default)
            logger.debug(f"Getting state for {component_id}: {value}")
            return value

    def clear_components(self):
        """Clear all components from the layout manager"""
        self._layout_manager.clear_layout()
