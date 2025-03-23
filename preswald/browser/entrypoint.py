"""
Entry point for Preswald in browser environments.
This module initializes the Pyodide environment and exposes
Python functionality to JavaScript.
"""

import logging
import sys
from typing import Any, Optional


# Configure logging for browser environment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verify we're in Pyodide
IS_PYODIDE = "pyodide" in sys.modules
if not IS_PYODIDE:
    logger.error("This module should only be imported in a Pyodide environment")
    sys.exit(1)

# Import required Pyodide-specific modules
from js import console, window  # type: ignore # noqa: E402


# Global service instance
_service = None
_script_runner = None
_client_id = "browser-client"


async def initialize_preswald(script_path: Optional[str] = None):
    """Initialize the Preswald service in the browser"""
    global _service, _script_runner, _client_id

    try:
        # Import the service
        from preswald.engine.service import PreswaldService

        # Initialize the service
        _service = PreswaldService.initialize(script_path)

        # Register a client
        _script_runner = await _service.register_client(_client_id)

        if _service and hasattr(_service, "branding_manager"):
            branding = _service.branding_manager.get_branding_config(script_path or "")

            import json

            branding_json = json.dumps(branding)

            # Set as string property on window
            window.PRESWALD_BRANDING = branding_json
            console.log(f"Set PRESWALD_BRANDING as JSON string: {branding_json}")

        logger.info(f"Preswald initialized in browser with script: {script_path}")
        console.log("Preswald initialized in browser")

        # Return success
        return {"success": True, "message": "Preswald initialized successfully"}
    except Exception as e:
        logger.error(f"Error initializing Preswald: {e}")
        console.error(f"Error initializing Preswald: {e!s}")
        return {"success": False, "error": str(e)}


async def run_script(script_path: str):
    """Run a script in the Preswald environment"""
    global _service, _script_runner

    if not _service:
        result = await initialize_preswald()
        if not result["success"]:
            return result

    try:
        # Update script path
        _service.script_path = script_path

        # Run the script
        if _script_runner:
            await _script_runner.start(script_path)
            return {"success": True, "message": f"Script executed: {script_path}"}
        else:
            return {"success": False, "error": "Script runner not initialized"}
    except Exception as e:
        logger.error(f"Error running script: {e}")
        return {"success": False, "error": str(e)}


async def update_component(component_id: str, value: Any):
    """Update a component's value"""
    global _service, _client_id

    if not _service:
        return {"success": False, "error": "Preswald not initialized"}

    try:
        # Create state update
        states = {component_id: value}

        # Handle the update
        await _service.handle_client_message(
            _client_id, {"type": "component_update", "states": states}
        )

        return {"success": True, "message": f"Component {component_id} updated"}
    except Exception as e:
        logger.error(f"Error updating component: {e}")
        return {"success": False, "error": str(e)}


async def shutdown():
    """Shut down the Preswald service"""
    global _service

    if not _service:
        return {
            "success": True,
            "message": "Preswald not initialized, nothing to shut down",
        }

    try:
        await _service.shutdown()
        return {"success": True, "message": "Preswald shut down successfully"}
    except Exception as e:
        logger.error(f"Error shutting down Preswald: {e}")
        return {"success": False, "error": str(e)}


async def deploy(github_username: str, api_key: str):
    """Dummy deploy function"""
    global _service

    if not _service:
        return {"success": False, "error": "Preswald not initialized"}

    try:
        console.log(
            f"from entrypoint.py -- Deployment in progress for {github_username}... {api_key}"
        )
        logger.info(
            f"from entrypoint.py -- Deployment in progress for {github_username}... {api_key}"
        )

        import asyncio

        await asyncio.sleep(2)  # Simulating deployment time delay

        console.log("Deployment successful!")
        logger.info("Dummy deployment completed.")

        return {"success": True, "message": "https://structuredlabs.com"}  # Updated URL
    except Exception as e:
        logger.error(f"Error during deployment: {e}")
        return {"success": False, "error": str(e)}


def expose_to_js():
    """Expose Python functions to JavaScript"""
    import asyncio

    # from js import window  # type: ignore
    from pyodide.ffi import create_proxy, to_js  # type: ignore

    def wrap_async_function(func):
        """Wrap an async function to be callable from JavaScript, handling both with and without arguments"""

        async def wrapper(*args, **kwargs):
            future = asyncio.ensure_future(func(*args, **kwargs))
            return to_js(future)

        return create_proxy(wrapper)

    # Export functions to JavaScript

    window.preswaldInit = wrap_async_function(initialize_preswald)
    window.preswaldRunScript = wrap_async_function(run_script)
    window.preswaldUpdateComponent = wrap_async_function(update_component)
    window.preswaldShutdown = wrap_async_function(shutdown)
    window.preswaldDeploy = wrap_async_function(deploy)

    # Message handling from JS to Python
    def handle_js_message(client_id, message_type, data):
        """Handle message from JavaScript"""
        if _service:
            asyncio.create_task(  # noqa: RUF006
                _service.handle_client_message(
                    client_id, {"type": message_type, "data": data}
                )
            )
        return True

    window.handleMessageFromJS = create_proxy(handle_js_message)

    console.log("Preswald Python API exposed to JavaScript")


# Auto-expose functions when module is imported
expose_to_js()
console.log("Preswald browser entrypoint loaded")
