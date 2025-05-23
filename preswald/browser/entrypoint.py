"""
Entry point for Preswald in browser environments.
This module initializes the Pyodide environment and exposes
Python functionality to JavaScript.
"""

import logging
import os
import shutil
import sys
import tempfile
from typing import Any


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


async def initialize_preswald(script_path: str | None = None):
    """Initialize the Preswald service in the browser"""
    global _service, _script_runner, _client_id

    try:
        # Import the service
        from preswald.engine.managers.branding import BrandingManager
        from preswald.engine.service import PreswaldService

        # Initialize the service
        _service = PreswaldService.initialize(script_path)

        # Register a client
        _script_runner = await _service.register_client(_client_id)

        # Set branding
        _service.branding_manager = BrandingManager(
            static_dir="",
            branding_dir="images",
        )

        if _service and hasattr(_service, "branding_manager"):
            branding = _service.branding_manager.get_branding_config_with_data_urls(
                script_path or ""
            )

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


async def export_html(script_path: str, client_type: str = "postmessage"):
    """Export the current Preswald app as an HTML package."""
    global _service
    if not _service:
        # Attempt to initialize if not already
        init_result = await initialize_preswald(script_path)
        if not init_result["success"]:
            return init_result  # Return initialization error

    logger.info(f"Starting HTML export for script: {script_path}")
    # Pyodide's FS is in-memory, tempfile.mkdtemp() works as expected.
    temp_export_dir = tempfile.mkdtemp(prefix="preswald_export_")
    logger.info(f"Created temporary export directory: {temp_export_dir}")

    try:
        from preswald.utils import prepare_html_export  # Import the utility function

        # Define the project root within Pyodide's virtual filesystem
        project_root_in_pyodide = "/project"

        # Call the centralized function to prepare all export files in temp_export_dir
        # script_path here is typically like "/project/app.py"
        prepare_html_export(
            script_path=script_path,
            output_dir=temp_export_dir,
            project_root_dir=project_root_in_pyodide,
            client_type=client_type,
        )

        # After prepare_html_export, collect all files from temp_export_dir into a dictionary
        exported_files = {}
        for root, _, files in os.walk(temp_export_dir):
            for file_name in files:
                file_path_abs = os.path.join(root, file_name)
                # Create a relative path for the dictionary keys (e.g., "index.html", "assets/main.js")
                relative_path = os.path.relpath(file_path_abs, temp_export_dir)
                try:
                    with open(file_path_abs, "rb") as f:  # Read as bytes
                        exported_files[relative_path] = f.read()
                except Exception as e:
                    logger.error(f"Error reading file {file_path_abs} for export: {e}")
                    # Store error message as content (bytes)
                    exported_files[relative_path] = f"Error reading file: {e}".encode()

        logger.info(
            f"Collected {len(exported_files)} files from {temp_export_dir} for browser export."
        )
        return {
            "success": True,
            "files": exported_files,
            "message": "HTML export generated successfully.",
        }

    except Exception as e:
        logger.error(f"Error during HTML export: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
    finally:
        if os.path.exists(temp_export_dir):
            shutil.rmtree(temp_export_dir)
            logger.info(f"Cleaned up temporary export directory: {temp_export_dir}")


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
    window.preswaldExportHtml = wrap_async_function(export_html)  # Expose new function

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
