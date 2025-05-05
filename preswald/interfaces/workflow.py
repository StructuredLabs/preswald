import hashlib
import inspect
import logging
import pickle
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Optional

import networkx as nx
import plotly.graph_objects as go

from preswald.interfaces.tracked_value import TrackedValue


logger = logging.getLogger(__name__)


class AtomContext:
    def __init__(self, workflow, atom_name):
        self.workflow = workflow
        self.atom_name = atom_name

    def __repr__(self):
        return f"AtomContext({self.atom_name})"


class AtomStatus(Enum):
    """Represents the current status of an atom's execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    SKIPPED = "skipped"


@dataclass
class AtomResult:
    """Represents the result of an atom's execution."""

    status: AtomStatus
    value: Any = None
    error: Exception | None = None
    attempts: int = 0
    start_time: float | None = None
    end_time: float | None = None
    input_hash: str | None = None

    @property
    def execution_time(self) -> float | None:
        """Calculate the execution time if both start and end times are available."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class RetryPolicy:
    """Defines how retries should be handled for failed atoms."""

    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        retry_exceptions: tuple = (Exception,),
    ):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.retry_exceptions = retry_exceptions

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Determine if another retry attempt should be made."""
        return attempt < self.max_attempts and isinstance(error, self.retry_exceptions)

    def get_delay(self, attempt: int) -> float:
        """Calculate the delay before the next retry attempt."""
        return self.delay * (self.backoff_factor ** (attempt - 1))


class AtomCache:
    """Manages caching of atom results and determines when recomputation is needed."""

    def __init__(self):
        self.cache: dict[str, AtomResult] = {}
        self.hash_cache: dict[str, str] = {}

    def compute_input_hash(self, atom_name: str, kwargs: dict[str, Any]) -> str:
        """
        Generate a stable hash from the atom name, its parameters,
        and hashes of dependencies to detect when recomputation is needed.
        """
        hash_items = [
            atom_name,
            sorted([(k, self._hash_value(v)) for k, v in kwargs.items()]),
        ]
        hash_str = str(hash_items).encode("utf-8")
        return hashlib.sha256(hash_str).hexdigest()

    def _hash_value(self, value: Any) -> str:
        """
        Create a hash for the input value. Pickle it when possible,
        fallback to using the object id for non-picklable objects.
        """
        try:
            return hashlib.sha256(pickle.dumps(value)).hexdigest()
        except Exception:
            return str(id(value))

    def should_recompute(self, atom_name: str, input_hash: str) -> bool:
        """Return True if the input hash has changed since last execution."""
        if atom_name not in self.cache:
            return True
        return self.cache[atom_name].input_hash != input_hash


@dataclass
class Atom:
    """
    Represents a cell/atom in the workflow DAG, with a callable,
    dependency list, and optional retry policy.
    """

    name: str
    func: Callable
    original_func: Callable
    dependencies: list[str] = field(default_factory=list)
    retry_policy: RetryPolicy | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    force_recompute: bool = False  # Flag to force recomputation regardless of cache

    def __post_init__(self):
        # Extract function signature to understand inputs
        self.signature = inspect.signature(self.func)
        # Set default retry policy if none provided
        if self.retry_policy is None:
            self.retry_policy = RetryPolicy()

        # Store the original function
        self.original_func = self.func

        # Create the wrapped function
        @wraps(self.original_func)
        def wrapped_func(*args, **kwargs):
            start_time = time.time()
            try:
                result = self.original_func(*args, **kwargs)
                logger.debug(f"Atom {self.name} completed successfully")
                return result
            except Exception as e:
                logger.error(
                    f"Atom {self.name} failed with error: {e!s}", exc_info=True
                )
                raise
            finally:
                end_time = time.time()
                execution_time = end_time - start_time
                logger.debug(f"Atom {self.name} execution time: {execution_time:.2f}s")

        # Replace the function with the wrapped version
        self.func = wrapped_func


class WorkflowContext:
    """
    Maintains the state and variables across atoms in the workflow.
    """

    def __init__(self):
        self.variables: dict[str, Any] = {}
        self.results: dict[str, AtomResult] = {}

    def get_variable(self, name: str) -> Any:
        return self.variables.get(name)

    def set_variable(self, name: str, value: Any):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"[CONTEXT] Set variable for {producer_atom} = {new_value}")
        self.variables[name] = value

    def set_result(self, atom_name: str, result: AtomResult):
        self.results[atom_name] = result
        if result.status == AtomStatus.COMPLETED:
            self.variables[atom_name] = result.value
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"[CONTEXT] Set result for {atom_name} = {result.value}")

class Workflow:
    """
    Core workflow engine that manages registration and execution of reactive atoms.
    """

    def __init__(self, service: Optional["BasePreswaldService"] = None, default_retry_policy: Optional[RetryPolicy] = None):
        self.atoms: dict[str, Atom] = {}
        self.context = WorkflowContext()
        self.default_retry_policy = default_retry_policy or RetryPolicy()
        self.cache = AtomCache()
        self._component_producers: dict[str, str] = {}  # component_id -> atom_name
        self._current_atom: str | None = None  # currently executing atom
        self._service = service
        self._is_rerun = False
        self._auto_atom_registry: dict[str, Callable] = {}
        self._registered_reactive_atoms: list[Callable] = []

    def atom(
        self,
        dependencies: list[str] | None = None,
        retry_policy: RetryPolicy | None = None,
        force_recompute: bool = False,
        name: str | None = None,
    ):
        """
        Decorator to manually register a function as a reactive atom in the workflow.

        Atoms can be registered either explicitly using this decorator
        or automatically through code transformation at runtime.

        If dependencies are not explicitly provided, they will be inferred
        from the function's parameter names.

        TODO: provide example usage before PR comes out of draft

        Args:
            dependencies (list[str], optional):
                Explicit list of atom names this atom depends on. If omitted, inferred from function arguments.
            retry_policy (RetryPolicy, optional):
                Custom retry policy to apply when this atom fails.
            force_recompute (bool, optional):
                If True, forces this atom to recompute even if inputs have not changed.
            name (str, optional):
                Custom name for the atom. Defaults to the function's name.
        """
        def decorator(func):
            atom_name = name or func.__name__

            if self._is_rerun and atom_name in self.atoms:
                logger.debug(f"[workflow.atom] Skipping re-registration during rerun {atom_name=}")
                return func

            logger.info(f"[workflow.atom] Registered atom {atom_name=}")

            # Use the unwrapped function to infer dependencies
            raw_func = getattr(func, 'original_func', func)
            inferred_deps = [
                k for k, v in inspect.signature(raw_func).parameters.items()
                if v.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            ]
            atom_deps = dependencies if dependencies is not None else inferred_deps

            atom = Atom(
                name=atom_name,
                original_func=func,
                func=func,
                dependencies=list(atom_deps),
                retry_policy=retry_policy or self.default_retry_policy,
                force_recompute=force_recompute,
            )
            self.atoms[atom_name] = atom

            logger.info(f"[DAG] Atom registration complete {atom_name=} -> {atom_deps=}")
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"[DAG] Current DAG state {[(a.name, list(a.dependencies)) for a in self.atoms.values()]}")

            return func

        return decorator

    def execute(
        self, recompute_atoms: set[str] | None = None
    ) -> dict[str, AtomResult]:
        """
        Executes atoms in the workflow, with selective recomputation.

        Args:
            recompute_atoms: Optional set of atom names to force recomputation,
                           regardless of cache status
        """
        self._is_rerun = True  # prevent duplicate re-registration
        try:
            # Clear caches and component producers, but not atoms
            self.cache.cache.clear()
            self._component_producers.clear()

            execution_order = self._get_execution_order()
            atoms_to_recompute = self._get_affected_atoms(recompute_atoms or set())

            logger.info(f"[DAG] Atoms to recompute {atoms_to_recompute=}")

            for atom_name in execution_order:
                if self._is_rerun and recompute_atoms and atom_name not in atoms_to_recompute:
                    logger.info(f"[DAG] Skipping atom (not affected) {atom_name=}")
                    continue

                atom = self.atoms[atom_name]
                if atom_name in atoms_to_recompute:
                    atom.force_recompute = True

                result = self._execute_atom(atom)
                self.context.set_result(atom_name, result)
                atom.force_recompute = False

                if result.status == AtomStatus.FAILED:
                    logger.error(f"[DAG] Execution halted due to failure {atom_name=}")
                    break

            return self.context.results
        finally:
            self._is_rerun = False

    def execute_relevant_atoms(self):
        """
        Execute top-level atoms (atoms with no dependencies).
        This mimics natural script execution by triggering leaf atoms,
        allowing dependencies to propagate automatically.
        """
        top_level_atoms = [name for name, atom in self.atoms.items() if not atom.dependencies]
        logger.debug(f"[workflow] Executing top-level atoms {top_level_atoms=}")
        for atom_name in top_level_atoms:
            try:
                logger.debug(f"[workflow] Triggering top-level atom {atom_name=}")
                atom = self.atoms[atom_name]
                result = self._execute_atom(atom)
                self.context.set_result(atom_name, result)
            except Exception as e:
                logger.warning(f"[workflow] Failed to execute top-level atom {atom_name=} {e=}", exc_info=True)

    def get_component_producer(self, component_id: str) -> str | None:
        """Return atom that produced a given component ID."""
        return self._component_producers.get(component_id)

    def register_component_producer(self, component_id: str, atom_name: str):
        """Link a component ID to its producing atom for DAG traceability."""
        logger.info(f"[DAG] Registering component producer {component_id=} {atom_name=}")
        self._component_producers[component_id] = atom_name
        if self._current_atom:
            logger.info(f"[DAG] Component registered while atom was active {self._current_atom=}")

    def _get_affected_atoms(self, changed_atoms: set[str]) -> set[str]:
        """
        Return the full set of atoms affected by a change to any atom in `changed_atoms`.
        """
        affected = set(changed_atoms)
        logger.info(f"[DAG] Starting recompute traversal {changed_atoms=}")

        while True:
            new_affected = {
                name for name, atom in self.atoms.items()
                if name not in affected and any(dep in affected for dep in atom.dependencies)
            }
            if not new_affected:
                break
            affected.update(new_affected)

        return affected

    def _validate_dependencies(self):
        """
        Validate all atoms reference valid dependencies and no cycles exist.
        """
        for atom in self.atoms.values():
            for dep in atom.dependencies:
                if dep not in self.atoms:
                    raise ValueError(f"Atom '{atom.name}' depends on missing atom '{dep}'")

        visited = set()
        temp_visited = set()
        stack = []

        def has_cycle(atom_name: str) -> bool:
            if atom_name in temp_visited:
                logger.error(f"[DAG] Cycle detected -> {' -> '.join([*stack, atom_name])}")
                return True
            if atom_name in visited:
                return False

            temp_visited.add(atom_name)
            stack.append(atom_name)

            for dep in self.atoms[atom_name].dependencies:
                if has_cycle(dep):
                    return True

            temp_visited.remove(atom_name)
            visited.add(atom_name)
            stack.pop()
            return False

        for atom_name in self.atoms:
            if has_cycle(atom_name):
                raise ValueError("Cycle detected in DAG")

    def _get_execution_order(self) -> list[str]:
        """Returns a valid execution order for atoms based on dependencies."""
        self._validate_dependencies()

        visited = set()
        order = []

        def visit(atom_name: str):
            if atom_name in visited:
                return

            for dep in self.atoms[atom_name].dependencies:
                visit(dep)

            visited.add(atom_name)
            order.append(atom_name)

        for atom_name in self.atoms:
            visit(atom_name)

        logger.info(f"[DAG] Computed atom execution order: {order}")

        return order

    def _execute_atom(self, atom: Atom, **kwargs) -> AtomResult:
        """
        Execute a single atom with caching and retry support.

        - Prepares input arguments from dependencies.
        - Skips execution if cached inputs match.
        - Retries execution on failure based on the atom's retry policy.
        """
        dependency_values = {
            dep: (
                self.context.variables[dep].value
                if isinstance(self.context.variables[dep], TrackedValue)
                else self.context.variables[dep]
            )
            for dep in atom.dependencies
            if dep in self.context.variables
        }

        input_hash = self.cache.compute_input_hash(atom.name, dependency_values)
        if not atom.force_recompute and not self.cache.should_recompute(atom.name, input_hash):
            cached_result = self.cache.cache[atom.name]
            cached_result.status = AtomStatus.SKIPPED
            return cached_result
            logger.info(f"[DAG] Using cached result {atom.name=}")

        self._current_atom = atom.name

        try:
            if self._service:
                with self._service.active_atom(atom.name):
                    return self._execute_atom_inner(atom, dependency_values, input_hash)
            else:
                return self._execute_atom_inner(atom, dependency_values, input_hash)
        finally:
            self._current_atom = None

    def _execute_atom_inner(self, atom: Atom, dependency_values: dict[str, Any], input_hash: str) -> AtomResult:
        """Actual retry-wrapped execution of atom logic."""
        attempts = 0
        start_time = time.time()

        while True:
            attempts += 1
            try:

                args = []
                missing_args = []

                for atom_dep in atom.dependencies:
                    if atom_dep in dependency_values:
                        args.append(dependency_values[atom_dep])
                    else:
                        missing_args.append(atom_dep)

                if missing_args:
                    logger.warning(f"[DAG] Atom {atom.name} missing input arguments {missing_args=}")
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[DAG] Available dependency values {dependency_values=}")

                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[DAG] Executing atom {atom.name=} {args=}")

                result = atom.func(*args)

                end_time = time.time()
                atom_result = AtomResult(
                    status=AtomStatus.COMPLETED,
                    value=result,
                    attempts=attempts,
                    start_time=start_time,
                    end_time=end_time,
                    input_hash=input_hash,
                )

                self.cache.cache[atom.name] = atom_result
                return atom_result
            except Exception as e:
                current_time = time.time()
                if atom.retry_policy.should_retry(attempts, e):
                    delay = atom.retry_policy.get_delay(attempts)
                    logger.warning(f"[DAG] Atom execution failed, retrying {atom.name=} {attempts=} delay={delay:.2f}")
                    time.sleep(delay)
                else:
                    return AtomResult(
                        status=AtomStatus.FAILED,
                        error=e,
                        attempts=attempts,
                        start_time=start_time,
                        end_time=current_time,
                        input_hash=input_hash,
                    )

    def register_dependency(self, atom_name: str, dep_name: str):
        """Dynamically register a dependency between two atoms.

        This should be called when `atom_name` reads a value produced by `dep_name`,
        establishing a dependency so that future changes to `dep_name` will trigger
        recomputation of `atom_name`.

        In user code, this typically occurs when one atom references a variable returned
        by another atom.

        Args:
            atom_name (str): The atom currently executing and consuming a dependency.
            dep_name (str): The atom whose output was accessed and should be tracked as a dependency.
        """
        if atom_name in self.atoms:
            self.atoms[atom_name].dependencies.append(dep_name)
            logger.info(f"[DAG] Registered dependency {atom_name=} -> {dep_name=}")
        else:
            logger.warning(f"[DAG] Cannot register dependency for unknown atom {atom_name=}")

    def reset(self):
        """Fully reset the workflow."""
        self.atoms.clear()
        self.context.variables.clear()
        self.context.results.clear()
        self._component_producers.clear()
        self.cache.cache.clear()
        self._auto_atom_registry.clear()
        self._registered_reactive_atoms.clear()
        self._current_atom = None
        self._is_rerun = False

    def debug_print_dag(self):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[DAG DEBUG] Current DAG edges:")
            for atom in self.atoms.values():
                for dep in atom.dependencies:
                    logger.debug(f"[DAG DEBUG] {dep=} -> {atom.name=}")


class WorkflowAnalyzer:
    """
    Provides visualization and analysis capabilities for workflow structures.
    Uses Plotly for interactive visualization and NetworkX for graph algorithms.
    """

    def __init__(self, workflow):
        self.workflow = workflow
        self.graph = nx.DiGraph()
        self._last_analysis_time = None

        # Define color scheme for different atom statuses
        self.status_colors = {
            "pending": "#E8E8E8",  # Light Gray
            "running": "#72B0DD",  # Blue
            "completed": "#72B7B7",  # Teal
            "failed": "#B76E79",  # Rose
            "retry": "#FFB347",  # Orange
            "skipped": "#D7BDE2",  # Light Purple
            "not_executed": "#C8C8C8",  # Gray
        }

    def build_graph(self) -> nx.DiGraph:
        """
        Constructs a NetworkX graph representation of the workflow.
        Includes rich metadata for visualization and analysis.
        """
        self.graph.clear()

        # Add nodes (atoms) with their metadata
        for atom_name, atom in self.workflow.atoms.items():
            result = self.workflow.context.results.get(atom_name)

            # Prepare node metadata with rich information for tooltips
            node_data = {
                "name": atom_name,
                "status": result.status.value if result else "not_executed",
                "execution_time": (
                    f"{result.execution_time:.2f}s"
                    if result and result.execution_time
                    else "N/A"
                ),
                "attempts": result.attempts if result else 0,
                "error": str(result.error) if result and result.error else None,
                "dependencies": list(atom.dependencies),
                "force_recompute": atom.force_recompute,
            }

            self.graph.add_node(atom_name, **node_data)

            # Add edges for dependencies
            for dep in atom.dependencies:
                self.graph.add_edge(dep, atom_name)

        self._last_analysis_time = datetime.now()
        return self.graph

    def get_critical_path(self) -> list[str]:
        """
        Identifies the critical path through the workflow - the longest dependency chain
        that must be executed sequentially.
        """
        if not self._is_graph_current():
            self.build_graph()

        try:
            # Find all paths and their total execution times
            paths = []
            for source in (n for n, d in self.graph.in_degree() if d == 0):
                for target in (n for n, d in self.graph.out_degree() if d == 0):
                    paths.extend(nx.all_simple_paths(self.graph, source, target))

            if not paths:
                return []

            # Calculate path weights based on execution times
            path_weights = []
            for path in paths:
                weight = sum(
                    (
                        float(self.graph.nodes[node]["execution_time"].rstrip("s"))
                        if self.graph.nodes[node]["execution_time"] != "N/A"
                        else 1.0
                    )
                    for node in path
                )
                path_weights.append((weight, path))

            return max(path_weights, key=lambda x: x[0])[1]

        except nx.NetworkXException as e:
            print(f"Error finding critical path: {e}")
            return []

    def get_parallel_groups(self) -> list[set[str]]:
        """
        Identifies groups of atoms that could potentially be executed in parallel.
        """
        if not self._is_graph_current():
            self.build_graph()

        try:
            return list(nx.topological_generations(self.graph))
        except nx.NetworkXException as e:
            print(f"Error finding parallel groups: {e}")
            return []

    def visualize(
        self,
        highlight_path: list[str] | None = None,
        title: str = "Workflow Dependency Graph",
    ):
        """
        Creates an interactive visualization of the workflow using Plotly.

        Args:
            highlight_path: Optional list of atom names to highlight (e.g., critical path)
            title: Title for the visualization
        """
        if not self._is_graph_current():
            self.build_graph()

        # Calculate layout using NetworkX
        pos = nx.spring_layout(self.graph, k=1, iterations=50)

        # Prepare node trace
        node_x, node_y = [], []
        node_colors, node_sizes = [], []
        node_texts = []

        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            # Get node status and set color
            status = self.graph.nodes[node]["status"]
            node_colors.append(
                self.status_colors.get(status, self.status_colors["not_executed"])
            )

            # Set node size (larger for highlighted path)
            size = 40 if highlight_path and node in highlight_path else 30
            node_sizes.append(size)

            # Create rich hover text
            hover_text = [
                f"Atom: {node}",
                f"Status: {status}",
                f"Execution Time: {self.graph.nodes[node]['execution_time']}",
                f"Attempts: {self.graph.nodes[node]['attempts']}",
            ]

            if self.graph.nodes[node]["error"]:
                hover_text.append(f"Error: {self.graph.nodes[node]['error']}")

            if self.graph.nodes[node]["dependencies"]:
                hover_text.append(
                    f"Dependencies: {', '.join(self.graph.nodes[node]['dependencies'])}"
                )

            node_texts.append("<br>".join(hover_text))

        nodes_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=list(self.graph.nodes()),
            textposition="bottom center",
            hovertext=node_texts,
            marker={
                "color": node_colors, "size": node_sizes, "line_width": 2, "line_color": "white"
            },
            name="Atoms",
        )

        # Prepare edge traces
        edge_traces = []

        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            # Determine if this edge is part of the highlighted path
            is_highlighted = (
                highlight_path
                and edge[0] in highlight_path
                and edge[1] in highlight_path
            )

            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode="lines",
                line={
                    "width": 3 if is_highlighted else 1,
                    "color": "#d62728" if is_highlighted else "#888",
                },
                hoverinfo="none",
                showlegend=False,
            )
            edge_traces.append(edge_trace)

        # Create the figure
        fig = go.Figure(
            data=[*edge_traces, nodes_trace],
            layout=go.Layout(
                title={"text": title, "x": 0.5, "y": 0.95},
                showlegend=False,
                hovermode="closest",
                margin={"b": 20, "l": 5, "r": 5, "t": 40},
                xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
                yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
                plot_bgcolor="white",
            ),
        )

        # Add a legend for node status colors
        for status, color in self.status_colors.items():
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker={"size": 10, "color": color},
                    name=status.replace("_", " ").title(),
                    showlegend=True,
                )
            )

        return fig

    def _is_graph_current(self) -> bool:
        """
        Checks if the current graph representation is up to date with the workflow state.
        """
        if self._last_analysis_time is None:
            return False

        for result in self.workflow.context.results.values():
            if (
                result.end_time
                and datetime.fromtimestamp(result.end_time) > self._last_analysis_time
            ):
                return False

        return True
