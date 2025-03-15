import os
import asyncio
import logging
import sys
import threading
import time
import traceback
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class ScriptState(Enum):
    """Manages the state of a running script."""

    INITIAL = "INITIAL"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


class ScriptRunner:
    def __init__(
        self,
        session_id: str,
        send_message_callback: Callable,
        initial_states: Dict = None,
    ):
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
            await self._send_message_callback(msg)
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

        try:
            await self.run_script()
        except Exception as e:
            await self._send_error(f"Failed to start script: {str(e)}")
            self._state = ScriptState.ERROR

    async def stop(self):
        """Stop the script and clean up resources."""
        try:
            logger.info(f"[ScriptRunner] Stopping script for session {self.session_id}")

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
                    logger.debug(
                        f"[ScriptRunner] Updated state: {component_id} = {value} (was {old_value})"
                    )

                self._run_count += 1
                self._last_run_time = current_time

            await self.run_script()

        except Exception as e:
            error_msg = f"Error updating widget states: {str(e)}"
            logger.error(f"[ScriptRunner] {error_msg}")
            await self._send_error(error_msg)
            self._state = ScriptState.ERROR

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
            await self.send_message({"type": "error", "content": error_content})
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
                                asyncio.create_task(
                                    self.callback(
                                        {"type": "output", "content": line + "\n"}
                                    )
                                )
                        self.buffer = lines[-1]

            def flush(self):
                with self._lock:
                    if self.buffer:
                        if self.buffer.strip():
                            logger.debug(
                                f"[ScriptRunner] Flushing output: {self.buffer}"
                            )
                            asyncio.create_task(
                                self.callback(
                                    {"type": "output", "content": self.buffer}
                                )
                            )
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

        try:
            from .service import PreswaldService
            service = PreswaldService.get_instance()
            
            # Clear previous components before execution
            service.clear_components()

            # Set up script environment
            self._script_globals = {
                "widget_states": self.widget_states,
            }

            # Capture script output
            with self._redirect_stdout():
                # Execute script
                with open(self.script_path, "r", encoding='utf-8') as f:
                    # Save current cwd
                    current_working_dir = os.getcwd()
                    # Execute script with script directory set as cwd
                    script_dir = os.path.dirname(os.path.realpath(self.script_path))
                    os.chdir(script_dir)
                    code = compile(f.read(), self.script_path, "exec")
                    logger.debug("[ScriptRunner] Script compiled")
                    exec(code, self._script_globals)
                    logger.debug("[ScriptRunner] Script executed")
                    # Change back to original working dir
                    os.chdir(current_working_dir)

                # Process rendered components
                components = service.get_rendered_components()
                logger.info(f"[ScriptRunner] Rendered {len(components)} components")

                if components:
                    # Send to frontend
                    await self.send_message(
                        {"type": "components", "components": components}
                    )
                    logger.debug("[ScriptRunner] Sent components to frontend")

        except Exception as e:
            error_msg = f"Error executing script: {str(e)}"
            logger.error(f"[ScriptRunner] {error_msg}", exc_info=True)
            await self._send_error(error_msg)
            self._state = ScriptState.ERROR
