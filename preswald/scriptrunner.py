import sys
import traceback
import logging
import threading
import asyncio
import time
from pathlib import Path
from contextlib import contextmanager
from typing import Dict, Callable, Optional, Any
from preswald.core import (
    update_component_state, 
    get_component_state, 
    get_all_component_states, 
    clear_rendered_components,
    clear_component_states
)

# Configure logging with more structured format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScriptState:
    """Manages the state of a running script."""
    INITIAL = "INITIAL"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"

class ScriptRunner:
    def __init__(self, session_id: str, send_message_callback: Callable, initial_states: Dict = None):
        """Initialize the ScriptRunner with enhanced state management.
        
        Args:
            session_id: Unique identifier for this session
            send_message_callback: Async callback to send messages to frontend
            initial_states: Initial widget states if any
        """
        self.session_id = session_id
        self._send_message_callback = send_message_callback
        self.script_path: Optional[str] = None
        self.widget_states = initial_states or {}
        self.session_state = {}
        self._state = ScriptState.INITIAL
        self._last_run_time = 0
        self._run_count = 0
        self._lock = threading.Lock()
        self._script_globals = {}
        
        logger.info(f"[ScriptRunner] Initialized with session_id: {session_id}")
        if initial_states:
            logger.debug(f"[ScriptRunner] Loaded initial states: {initial_states}")

    async def send_message(self, msg: dict):
        """Send a message to the frontend."""
        try:
            self._send_message_callback(msg)
        except Exception as e:
            logger.error(f"[ScriptRunner] Error sending message: {e}")

    @property
    def is_running(self) -> bool:
        """Thread-safe check if script is running."""
        with self._lock:
            return self._state == ScriptState.RUNNING

    async def start(self, script_path: str):
        """Start running the script with enhanced validation.
        
        Args:
            script_path: Path to the script file to run
        """
        script_file = Path(script_path)
        if not script_file.exists():
            error_msg = f"Script file not found: {script_path}"
            logger.error(f"[ScriptRunner] {error_msg}")
            await self._send_error(error_msg)
            return

        logger.info(f"[ScriptRunner] Starting execution: {script_path}")
        with self._lock:
            self.script_path = script_path
            self._state = ScriptState.RUNNING
            self._run_count = 0
        
        # Initialize core states
        try:
            for component_id, value in self.widget_states.items():
                update_component_state(component_id, value)
                logger.debug(f"[ScriptRunner] Initialized state: {component_id} = {value}")
            
            await self.run_script()
        except Exception as e:
            await self._send_error(f"Failed to start script: {str(e)}")
            self._state = ScriptState.ERROR

    async def stop(self):
        """Stop the script and clean up resources."""
        try:
            logger.info(f"[ScriptRunner] Stopping script for session {self.session_id}")
            
            # Clean up any resources
            clear_rendered_components()
            clear_component_states()
            
            # Clean up connections created by this session
            from preswald.core import connections, disconnect
            for name in list(connections.keys()):
                if name.startswith(f"connection_{self.session_id}"):
                    try:
                        disconnect(name)
                    except Exception as e:
                        logger.error(f"[ScriptRunner] Error cleaning up connection {name}: {e}")
            
            self._state = ScriptState.STOPPED
            logger.info(f"[ScriptRunner] Script stopped for session {self.session_id}")
        except Exception as e:
            logger.error(f"[ScriptRunner] Error stopping script: {e}")
            raise

    async def rerun(self, new_widget_states: Dict[str, Any] = None):
        """Rerun the script with new widget values and debouncing.
        
        Args:
            new_widget_states: Dictionary of widget ID to new value
        """
        if not new_widget_states:
            logger.debug("[ScriptRunner] No new states for rerun")
            return

        # Basic debouncing - skip if last run was too recent
        current_time = time.time()
        if current_time - self._last_run_time < 0.1:  # 100ms debounce
            logger.debug("[ScriptRunner] Skipping rerun due to debounce")
            return

        logger.info(f"[ScriptRunner] Rerunning with new states: {new_widget_states}")
        
        try:
            # Update states atomically
            with self._lock:
                for component_id, value in new_widget_states.items():
                    old_value = self.widget_states.get(component_id)
                    self.widget_states[component_id] = value
                    update_component_state(component_id, value)
                    logger.debug(f"[ScriptRunner] Updated state: {component_id} = {value} (was {old_value})")
                
                self._run_count += 1
                self._last_run_time = current_time
            
            # Clear components before rerun
            clear_rendered_components()
            clear_component_states()
            await self.run_script()
            
        except Exception as e:
            error_msg = f"Error updating widget states: {str(e)}"
            logger.error(f"[ScriptRunner] {error_msg}")
            await self._send_error(error_msg)
            self._state = ScriptState.ERROR

    async def _cleanup(self):
        """Clean up resources when stopping the script."""
        try:
            clear_rendered_components()
            clear_component_states()
            self._script_globals.clear()
            self.session_state.clear()
            logger.info("[ScriptRunner] Cleanup completed")
        except Exception as e:
            logger.error(f"[ScriptRunner] Error during cleanup: {e}")

    async def _send_error(self, message: str, include_traceback: bool = True):
        """Send error message to frontend.
        
        Args:
            message: Error message to send
            include_traceback: Whether to include stack trace
        """
        try:
            error_content = {
                "message": message,
                "stack_trace": traceback.format_exc() if include_traceback else None,
            }
            await self.send_message({
                "type": "error",
                "content": error_content
            })
        except Exception as e:
            logger.error(f"[ScriptRunner] Failed to send error message: {e}")

    @contextmanager
    def _redirect_stdout(self):
        """Capture and redirect stdout with improved buffering."""
        logger.debug("[ScriptRunner] Setting up stdout redirection")
        
        class PreswaldOutputStream:
            def __init__(self, callback):
                self.callback = callback
                self.buffer = ""
                self._lock = threading.Lock()

            def write(self, text):
                with self._lock:
                    self.buffer += text
                    if "\n" in self.buffer:
                        lines = self.buffer.split("\n")
                        for line in lines[:-1]:
                            if line.strip():
                                logger.debug(f"[ScriptRunner] Captured output: {line}")
                                asyncio.create_task(self.callback({
                                    "type": "output",
                                    "content": line + "\n"
                                }))
                        self.buffer = lines[-1]

            def flush(self):
                with self._lock:
                    if self.buffer:
                        if self.buffer.strip():
                            logger.debug(f"[ScriptRunner] Flushing output: {self.buffer}")
                            asyncio.create_task(self.callback({
                                "type": "output",
                                "content": self.buffer
                            }))
                        self.buffer = ""

        old_stdout = sys.stdout
        output_stream = PreswaldOutputStream(self.send_message)
        sys.stdout = output_stream
        try:
            yield
        finally:
            output_stream.flush()
            sys.stdout = old_stdout
            logger.debug("[ScriptRunner] Restored stdout")

    async def run_script(self):
        """Execute the script with enhanced error handling and state management."""
        if not self.is_running or not self.script_path:
            logger.warning("[ScriptRunner] Not running or no script path set")
            return

        logger.info(f"[ScriptRunner] Running script: {self.script_path} (run #{self._run_count})")
        
        # Set up script environment
        self._script_globals = {
            "session_state": self.session_state,
            "widget_states": self.widget_states,
        }

        try:
            from preswald.core import _rendered_html, get_rendered_components
            
            # Capture script output
            with self._redirect_stdout():
                # Execute script
                with open(self.script_path, "r") as f:
                    code = compile(f.read(), self.script_path, "exec")
                    logger.debug("[ScriptRunner] Script compiled")
                    exec(code, self._script_globals)
                    logger.debug("[ScriptRunner] Script executed")

                # Process rendered components
                components = get_rendered_components()
                logger.info(f"[ScriptRunner] Rendered {len(components)} components")

                if components:
                    # Update component states
                    for component in components:
                        if 'id' in component:
                            current_state = self.widget_states.get(
                                component['id'],
                                get_component_state(component['id'])
                            )
                            if current_state is not None and 'value' in component:
                                component['value'] = current_state
                                logger.debug(f"[ScriptRunner] Set component {component['id']} value: {current_state}")

                    # Send to frontend
                    await self.send_message({
                        "type": "components",
                        "components": components
                    })
                    logger.debug("[ScriptRunner] Sent components to frontend")

        except Exception as e:
            error_msg = f"Error executing script: {str(e)}"
            logger.error(f"[ScriptRunner] {error_msg}", exc_info=True)
            await self._send_error(error_msg)
            self._state = ScriptState.ERROR
