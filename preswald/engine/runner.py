import asyncio
import builtins
import logging
import os
import sys
import threading
import time
import traceback
from collections.abc import Callable
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Any

from preswald.engine.transformers.reactive_runtime import transform_source
from preswald.utils import reactivity_explicitly_disabled


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
        initial_states: dict | None = None,
    ):
        """Initialize the ScriptRunner with enhanced state management.

        Args:
            session_id: Unique identifier for this session
            send_message_callback: Async callback to send messages to frontend
            initial_states: Initial widget states if any
        """
        self.session_id = session_id
        self._send_message_callback = send_message_callback
        self.script_path: str | None = None
        self.widget_states = initial_states or {}
        self._state = ScriptState.INITIAL
        self._last_run_time = 0
        self._run_count = 0
        self._lock = threading.Lock()
        self._script_globals = {}

        from .service import PreswaldService # deferred import to avoid cyclic dependency
        self._service = PreswaldService.get_instance()

        logger.info(f"[ScriptRunner] Initialized with session_id: {session_id}")
        if initial_states:
            logger.info(f"[ScriptRunner] Loaded initial states: {initial_states}")

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

        if reactivity_explicitly_disabled():
           self._service.disable_reactivity()
        else:
            logger.info("[ScriptRunner] Reactivity is disabled by configuration")

        try:
            await self.run_script()
        except Exception as e:
            await self._send_error(f"Failed to start script: {e!s}")
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

    async def rerun(self, new_widget_states: dict[str, Any] | None = None):
        """
        Rerun the script in response to updated widget state.

        This uses DAG-based dependency tracking (from AST instrumentation in Phase 3)
        to determine which atoms are affected and should be recomputed.

        Fallback to full rerun is triggered if affected atoms cannot be determined.

        Args:
            new_widget_states (dict[str, Any] | None): Updated component states (by ID).
        """

        # Basic debouncing - skip if last run was too recent
        current_time = time.time()
        if current_time - self._last_run_time < 0.1:
            logger.info("[ScriptRunner] Skipping rerun due to debounce")
            return

        if not new_widget_states:
            logger.info("[ScriptRunner] No new states for rerun")
            return

        if not self._service.is_reactivity_enabled:
            logger.info("[ScriptRunner] Reactivity disabled — rerunning entire script with updated widget state")
            return await self.run_script()

        try:
            with self._lock:
                for component_id, value in new_widget_states.items():
                    old_value = self.widget_states.get(component_id)
                    self.widget_states[component_id] = value
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[ScriptRunner] Updated state: {component_id=} -> {value=} (was {old_value=})")
                self._run_count += 1
                self._last_run_time = current_time

            # determine affected components and force recomputation
            changed_component_ids = set(new_widget_states.keys())
            workflow = self._service.get_workflow()

            changed_atoms = set()
            for cid in changed_component_ids:
                atom = workflow.get_component_producer(cid)
                if atom:
                    changed_atoms.add(atom)
                else:
                    logger.warning(f"[ScriptRunner] No producer found for component_id: {cid}")

            affected_atoms = workflow._get_affected_atoms(changed_atoms)

            # Inject updated widget states into workflow context before executing
            for component_id, new_value in self.widget_states.items():
                producer_atom = workflow.get_component_producer(component_id)
                if producer_atom:
                    workflow.context.set_variable(producer_atom, new_value)

            if not changed_atoms and not affected_atoms:
                logger.warning("[ScriptRunner] No atoms affected — falling back to full script rerun")
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[ScriptRunner] changed_atoms = {changed_atoms}, component_ids = {changed_component_ids}")

                # Fallback: reset all DAG and component state before rerunning
                self._service.disable_reactivity()
                workflow.reset()
                self._service.clear_components()
                self._script_globals = {
                    "__file__": self.script_path,
                    "workflow": workflow,
                    "widget_states": self.widget_states,
                }

                await self.run_script()
                return

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"[ScriptRunner] Rerun using DAG reactivity with {len(affected_atoms)} affected atoms")
                logger.debug(f"[ScriptRunner] {changed_atoms=}, {affected_atoms=}")

            self._service.force_recompute(affected_atoms)
            results = workflow.execute(recompute_atoms=affected_atoms)

            # Ensure layout rendering happens for all atoms
            for atom_name, result in results.items():
                with self._service.active_atom(atom_name):
                    if result is not None:
                        value = result.value if hasattr(result, 'value') else None
                        if (
                            hasattr(value, "_preswald_component_type")  # identifies a component created by with_render_tracking
                            or (isinstance(value, dict) and "type" in value)  # fallback safety
                        ):
                            self._service.append_component(value)
                        else:
                            logger.info(f"[ScriptRunner] Skipping non-component value for {atom_name=}")
                            if logger.isEnabledFor(logging.DEBUG):
                                logger.debug(f"[ScriptRunner] {atom_name=} -> {result!r}")

            components = self._service.get_rendered_components()
            logger.info(f"[ScriptRunner] Rendered {len(components)} components (rerun)")

            if components:
                await self.send_message({"type": "components", "components": components})
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[ScriptRunner] Sent components to frontend {components=}")
                else:
                    logger.info(f"[ScriptRunner] Sent components to frontend")

            logger.info(f"[ScriptRunner] Rerun completed in {time.time() - current_time:.2f}s (total)")
            workflow.debug_print_dag()

        except Exception as e:
            error_msg = f"Error updating widget states: {e!s}"
            logger.error(f"[ScriptRunner] {error_msg}", exc_info=True)
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
                                if logger.isEnabledFor(logging.DEBUG):
                                    logger.debug(f"[ScriptRunner] Captured output: {line}")
                                asyncio.create_task(  # noqa: RUF006
                                    self.callback(
                                        {"type": "output", "content": line + "\n"}
                                    )
                                )
                        self.buffer = lines[-1]

            def flush(self):
                with self._lock:
                    if self.buffer:
                        if self.buffer.strip():
                            if logger.isEnabledFor(logging.DEBUG):
                                logger.debug(
                                    f"[ScriptRunner] Flushing output: {self.buffer}"
                                )
                            asyncio.create_task(  # noqa: RUF006
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

    def run_sync(self, script_path: str):
        """Run the script synchronously for CLI tools like export."""
        import asyncio

        self.script_path = script_path
        self._state = ScriptState.RUNNING
        self._run_count = 1

        # block on the async `run_script()` method
        asyncio.run(self.run_script())

    async def run_script(self):
        """
        Execute the user script with a clean workflow state, AST transformation,
        dependency tracking, and final component collection.

        This prepares the runtime environment, executes the script with reactivity enabled,
        and sends generated components back to the frontend. If transformation fails,
        it falls back to executing the raw script without reactivity.
        """
        if not self.is_running or not self.script_path:
            logger.warning("[ScriptRunner] Not running or no script path set")
            return

        # Ensure we run the script from a clear state
        workflow = self._service.get_workflow()
        workflow.reset()

        logger.info(f"[ScriptRunner] Starting script execution {self.script_path=} {self._run_count=}")

        try:
            # Reset state and connect services
            self._service.clear_components()
            self._service.connect_data_manager()

            # Prepare script execution environment
            self._script_globals = {"widget_states": self.widget_states}

            # Capture script output
            with self._redirect_stdout():
                with open(self.script_path, encoding="utf-8") as f:
                    raw_code = f.read()

                current_working_dir = os.getcwd()
                script_dir = os.path.dirname(os.path.realpath(self.script_path))
                os.chdir(script_dir)

                def compile_and_run(src_code, script_path, script_globals, execution_context):
                    code = compile(src_code, script_path, "exec")
                    logger.debug(f"[ScriptRunner] Script compiled {script_path=}")
                    exec(code, script_globals)
                    logger.debug(f"[ScriptRunner] Script executed {execution_context}")

                try:
                    if self._service.is_reactivity_enabled:
                        # Attempt reactive transformation
                        tree, _ = transform_source(raw_code, filename=self.script_path)
                        self._script_globals["workflow"] = workflow
                        compile_and_run(tree, self.script_path, self._script_globals, "(reactive)")
                        workflow.execute_relevant_atoms()
                    else:
                        compile_and_run(raw_code, self.script_path, self._script_globals, "(non-reactive)")
                        workflow.reset() # just to be safe

                except Exception as transform_error:
                    if logger.isEnabledFor(logging.WARNING):
                        logger.warning(
                            "[ScriptRunner] AST transform or reactive execution failed — falling back to full script rerun\n%s",
                            traceback.format_exc()
                        )

                    self._service.disable_reactivity()
                    workflow.reset()
                    self._service.clear_components()
                    self._script_globals = {
                        "__file__": self.script_path,
                        "workflow": workflow,
                        "widget_states": self.widget_states,
                    }

                    compile_and_run(raw_code, self.script_path, self._script_globals, "(fallback, non-reactive)")

                os.chdir(current_working_dir)

            # Collect and process rendered components
            components = self._service.get_rendered_components()
            rows = components.get("rows", [])
            row_count = len(rows)
            logger.debug(f"[ScriptRunner] Rendered components {row_count=}")

            for row in rows:
                for component in row:
                    component_id = component.get("id")
                    if not component_id:
                        continue
                    producer_atom = workflow.get_component_producer(component_id)
                    if producer_atom:
                        with self._service.active_atom(producer_atom):
                            _ = self._service.get_component_state(component_id)
                    else:
                        logger.warning(f"[ScriptRunner] No producer atom found {component_id=}")
                        continue

            if components:
                await self.send_message({"type": "components", "components": components})
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[ScriptRunner] Components sent to frontend {components=}")
            workflow.debug_print_dag()

        except Exception as e:
            error_msg = f"Error executing script: {e!s}"
            logger.error(f"[ScriptRunner] {error_msg}", exc_info=True)
            await self._send_error(error_msg)
            self._state = ScriptState.ERROR
