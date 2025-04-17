"""
Browser compatibility layer for Preswald in Pyodide environments
"""

import asyncio
import logging
import sys
from typing import Any

from preswald.engine.base_service import BasePreswaldService
from preswald.engine.utils import RenderBuffer

from preswald.engine.base_service import BasePreswaldService
from preswald.engine.utils import RenderBuffer


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

    async def send_json(self, data: dict[str, Any]):
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


class VirtualPreswaldService(BasePreswaldService):
    """
    Browser-compatible implementation of PreswaldService that works in Pyodide
    without requiring FastAPI, uvicorn, or websockets.
    """

    _instance = None
    _not_initialized_msg = (
        "VirtualPreswaldService not initialized. Did you call initialize()?"
    )

    def __init__(self):
        """Initialize the service with browser-compatible components"""
        super().__init__()

        # Client connections (virtual)
        self.websocket_connections = {}

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

                asyncio.create_task(self.handle_client_message(client_id, message))  # noqa: RUF006
                return True
            except Exception:
                import traceback

                logger.error(
                    "Error in handle_message_from_js: %s", traceback.format_exc()
                )
                return False

        # Export the function to JavaScript
        handle_message_proxy = create_proxy(handle_message_from_js)

        window.handleMessageFromJS = handle_message_proxy

        console.log("Registered Python message handlers with JavaScript")

    async def register_client(self, client_id: str, websocket=None):
        """Register a client with the service"""
        try:
            # In browser, create a virtual websocket if none provided
            if websocket is None:
                websocket = VirtualWebSocket(client_id)

            # Accept the connection
            await websocket.accept()
            return await self._register_common_client_setup(client_id, websocket)

        except Exception as e:
            logger.error(f"Error registering client {client_id}: {e}")
            raise
