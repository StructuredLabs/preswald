import networkx as nx
from typing import Any, Dict, List, Optional, Set, Callable, Union
from dataclasses import dataclass, field
import inspect
import uuid
import time
from enum import Enum
import logging
from functools import wraps

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StateManager:
    def __init__(self):
        # Core data structures
        self.graph = nx.DiGraph()  # Stores function dependencies
        self.cache = {}  # Stores function results
        self.data_to_node = {}  # Maps data objects to their source nodes
        self.current_execution = None  # Tracks currently executing function

    def track_function_call(self, func, args, kwargs):
        print("tracking function call ", str(func))
        node_id = self._create_node_id(func, args, kwargs)
        print("tracking function call ", node_id)

        # Add node to graph if it doesn't exist
        if node_id not in self.graph:
            self.graph.add_node(node_id, func=func, args=args, kwargs=kwargs)

        # Track dependencies from two sources:

        # 1. Current execution context
        if self.current_execution:
            self.graph.add_edge(self.current_execution, node_id)

        # 2. Data object dependencies
        for arg in args:
            if arg in self.data_to_node:
                parent_node = self.data_to_node[arg]
                self.graph.add_edge(parent_node, node_id)

        for arg in kwargs.values():
            if arg in self.data_to_node:
                parent_node = self.data_to_node[arg]
                self.graph.add_edge(parent_node, node_id)

        return node_id

    def _create_node_id(self, func, args, kwargs):
        """Create a unique identifier for a function call"""
        # For now, a simple combination of function name and argument IDs
        arg_ids = [str(id(arg)) for arg in args]
        kwarg_ids = [f"{k}:{id(v)}" for k, v in kwargs.items()]
        return f"{func.__name__}_{'-'.join(arg_ids + kwarg_ids)}"

    def get_or_compute(self, node_id):
        """Get cached result or compute if necessary"""
        if node_id in self.cache:
            return self.cache[node_id]

        return self.execute(node_id)

    def execute(self, node_id):
        """Execute a function and cache its result"""
        # Set up execution context
        previous_execution = self.current_execution
        self.current_execution = node_id

        print("executing node ", node_id)

        try:
            # Get function and arguments
            node = self.graph.nodes[node_id]
            func = node["func"]
            args = node["args"]
            kwargs = node["kwargs"]

            # Execute function
            result = func(*args, **kwargs)

            # Cache result and track its source
            self.cache[node_id] = result
            self.data_to_node[result] = node_id

            return result
        finally:
            # Restore previous execution context
            self.current_execution = previous_execution

    def invalidate(self, node_id):
        """Invalidate a node and its descendants"""
        # Get all nodes that depend on this one
        descendants = nx.descendants(self.graph, node_id)
        affected_nodes = {node_id} | descendants

        # Remove them from cache
        for node in affected_nodes:
            self.cache.pop(node, None)


class AtomStatus(Enum):
    """Represents the current status of an atom's execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class AtomResult:
    """Represents the result of an atom's execution."""

    status: AtomStatus
    value: Any = None
    error: Optional[Exception] = None
    attempts: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    @property
    def execution_time(self) -> Optional[float]:
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


@dataclass
class Atom:
    """
    Represents a cell/atom in the workflow, containing code and its dependencies.
    """

    name: str
    func: Callable
    dependencies: Set[str] = field(default_factory=set)
    retry_policy: Optional[RetryPolicy] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        # Extract function signature to understand inputs
        self.signature = inspect.signature(self.func)
        # Set default retry policy if none provided
        if self.retry_policy is None:
            self.retry_policy = RetryPolicy()

        # Store the original function
        self._original_func = self.func

        # Wrap the function to add logging and timing
        @wraps(self.func)
        def wrapped_func(*args, **kwargs):
            logger.info(f"Executing atom: {self.name}")
            start_time = time.time()
            try:
                result = self._original_func(*args, **kwargs)
                logger.info(f"Atom {self.name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Atom {self.name} failed with error: {str(e)}", exc_info=True)
                raise
            finally:
                end_time = time.time()
                execution_time = end_time - start_time
                logger.info(f"Atom {self.name} execution time: {execution_time:.2f}s")

        self.func = wrapped_func


class WorkflowContext:
    """
    Maintains the state and variables across atoms in the workflow.
    """

    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.results: Dict[str, AtomResult] = {}

    def get_variable(self, name: str) -> Any:
        return self.variables.get(name)

    def set_variable(self, name: str, value: Any):
        self.variables[name] = value

    def set_result(self, atom_name: str, result: AtomResult):
        self.results[atom_name] = result
        if result.status == AtomStatus.COMPLETED:
            self.variables[atom_name] = result.value


class Workflow:
    """
    Main workflow class that manages atoms and their execution.
    """

    def __init__(self, default_retry_policy: Optional[RetryPolicy] = None):
        self.atoms: Dict[str, Atom] = {}
        self.context = WorkflowContext()
        self.default_retry_policy = default_retry_policy or RetryPolicy()

    def atom(
        self,
        dependencies: Optional[List[str]] = None,
        retry_policy: Optional[RetryPolicy] = None,
    ):
        """
        Decorator to create and register an atom in the workflow.

        @workflow.atom(dependencies=['atom1', 'atom2'])
        def my_atom(x, y):
            return x + y
        """

        def decorator(func):
            atom_name = func.__name__
            atom = Atom(
                name=atom_name,
                func=func,
                dependencies=set(dependencies or []),
                retry_policy=retry_policy or self.default_retry_policy,
            )
            self.atoms[atom_name] = atom
            return func

        return decorator

    def _validate_dependencies(self):
        """Validates that all dependencies exist and there are no cycles."""
        for atom in self.atoms.values():
            for dep in atom.dependencies:
                if dep not in self.atoms:
                    raise ValueError(
                        f"Atom '{atom.name}' depends on non-existent atom '{dep}'"
                    )

        # Check for cycles using DFS
        visited = set()
        temp_visited = set()

        def has_cycle(atom_name: str) -> bool:
            if atom_name in temp_visited:
                return True
            if atom_name in visited:
                return False

            temp_visited.add(atom_name)

            for dep in self.atoms[atom_name].dependencies:
                if has_cycle(dep):
                    return True

            temp_visited.remove(atom_name)
            visited.add(atom_name)
            return False

        for atom_name in self.atoms:
            if has_cycle(atom_name):
                raise ValueError("Circular dependency detected in workflow")

    def _get_execution_order(self) -> List[str]:
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

        return order

    def _execute_atom(self, atom: Atom, **kwargs) -> AtomResult:
        """Execute a single atom with retry logic."""
        attempts = 0
        start_time = time.time()

        while True:
            attempts += 1
            try:
                result = atom.func(**kwargs)
                end_time = time.time()
                return AtomResult(
                    status=AtomStatus.COMPLETED,
                    value=result,
                    attempts=attempts,
                    start_time=start_time,
                    end_time=end_time,
                )
            except Exception as e:
                current_time = time.time()
                if atom.retry_policy.should_retry(attempts, e):
                    logger.warning(
                        f"Atom {atom.name} failed (attempt {attempts}). "
                        f"Retrying after {atom.retry_policy.get_delay(attempts)}s"
                    )
                    time.sleep(atom.retry_policy.get_delay(attempts))
                    continue
                else:
                    return AtomResult(
                        status=AtomStatus.FAILED,
                        error=e,
                        attempts=attempts,
                        start_time=start_time,
                        end_time=current_time,
                    )

    def execute(self) -> Dict[str, AtomResult]:
        """Executes all atoms in the workflow in the correct order."""
        execution_order = self._get_execution_order()

        for atom_name in execution_order:
            atom = self.atoms[atom_name]

            # Prepare arguments for the atom based on its signature
            kwargs = {}
            for param_name in atom.signature.parameters:
                if param_name in self.context.variables:
                    kwargs[param_name] = self.context.variables[param_name]

            # Execute the atom with retry logic
            result = self._execute_atom(atom, **kwargs)

            # Store the result in the context
            self.context.set_result(atom_name, result)

            # If this atom failed and has dependencies, we should stop execution
            if result.status == AtomStatus.FAILED:
                logger.error(f"Workflow stopped due to failure in atom: {atom_name}")
                break

        return self.context.results
