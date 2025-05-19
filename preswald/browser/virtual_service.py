"""
Browser compatibility layer for Preswald in Pyodide environments
"""

import asyncio
import logging
import sys
from typing import Any

from preswald.engine.base_service import BasePreswaldService


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
        """
        Sends a JSON-serializable dictionary to the JavaScript frontend.

        Uses postMessage or handlePythonMessage depending on the environment.
        Logs only a summary of the data payload when debug logging is enabled.
        """
        if not self.is_connected:
            logger.error(f"Cannot send message, connection closed for {self.client_id}")
            return

        if not IS_PYODIDE:
            return

        debug_enabled = logger.isEnabledFor(logging.DEBUG)

        try:
            import json

            from js import JSON

            json_str = json.dumps(data)
            js_data = JSON.parse(json_str)

            if debug_enabled:
                summary = {
                    "keys": list(data.keys()),
                    "types": {k: type(v).__name__ for k, v in data.items()},
                }

            if self.is_browser_mode:
                from js import self as js_self  # type: ignore

                js_self.postMessage(js_data)
                if debug_enabled:
                    console.debug(
                        "[VirtualWebSocket] postMessage (browser mode) summary:",
                        summary,
                    )
            else:
                try:
                    from js import handlePythonMessage

                    handlePythonMessage(self.client_id, js_data)
                    if debug_enabled:
                        console.debug(
                            "[VirtualWebSocket] handlePythonMessage summary:", summary
                        )
                except ImportError:
                    from js import self as js_self

                    js_self.postMessage(js_data)
                    if debug_enabled:
                        console.debug(
                            "[VirtualWebSocket] postMessage (fallback) summary:",
                            summary,
                        )

        except Exception as e:
            logger.error(f"Error sending message to JS: {e}")

    async def send_bytes(self, data: bytes):
        """
        Sends binary data to the JavaScript frontend using either `postMessage` or `handlePythonBinaryMessage`.

        Logs a summary of the message (length only) in debug mode to avoid large console output.
        """
        if not self.is_connected:
            logger.error(f"Cannot send bytes, connection closed for {self.client_id}")
            return

        if not IS_PYODIDE:
            return

        debug_enabled = logger.isEnabledFor(logging.DEBUG)

        try:
            from js import window

            array = window.Uint8Array.new(len(data))
            for i, b in enumerate(data):
                array[i] = b

            if debug_enabled:
                summary = {
                    "length": len(data),
                    "first_byte": data[0] if data else None,
                    "last_byte": data[-1] if data else None,
                }

            if self.is_browser_mode:
                from js import self as js_self  # type: ignore

                js_self.postMessage({"type": "binary_message", "data": array})
                if debug_enabled:
                    console.debug(
                        "[VirtualWebSocket] postMessage (binary, browser mode) summary:",
                        summary,
                    )
            else:
                try:
                    from js import handlePythonBinaryMessage

                    handlePythonBinaryMessage(self.client_id, array)
                    if debug_enabled:
                        console.debug(
                            "[VirtualWebSocket] handlePythonBinaryMessage summary:",
                            summary,
                        )
                except ImportError:
                    from js import self as js_self

                    js_self.postMessage({"type": "binary_message", "data": array})
                    if debug_enabled:
                        logger.warning(
                            f"[{self.client_id}] handlePythonBinaryMessage not available, using postMessage fallback"
                        )
                        console.debug(
                            "[VirtualWebSocket] postMessage (binary fallback) summary:",
                            summary,
                        )

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
