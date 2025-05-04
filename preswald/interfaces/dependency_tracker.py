import logging


logger = logging.getLogger(__name__)

# Thread-local context stack for dependency tracking.
# This tracks the currently executing atom so that dynamic dependencies
# (like reading another atom's value during execution) can be recorded.

_context_stack = []


def get_current_context():
    """
    Get the currently active dependency tracking context, if any.

    Returns:
        The topmost context object from the stack, or None if the stack is empty.
    """
    return _context_stack[-1] if _context_stack else None


def track_dependency(dep_name: str):
    """
    Register a runtime dependency between the currently executing atom and another.

    This is typically invoked when an atom reads the value of another tracked value.
    The dependency is added to the DAG via the current context.

    Args:
        dep_name (str): The name of the dependency being accessed.
    """
    ctx = get_current_context()
    if ctx:
        logger.debug(f"[DAG] Registered dynamic dependency {{atom={ctx.atom_name}, dep={dep_name}}}")
        ctx.workflow.register_dependency(ctx.atom_name, dep_name)
    else:
        logger.warning(f"[DAG] Dependency tracking failed (no context) {{dep={dep_name}}}")


def push_context(ctx):
    """
    Push a new atom execution context onto the stack.

    Args:
        ctx: A context object with 'atom_name' and 'workflow' attributes.
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Pushing context for atom {ctx.atom_name}")
    _context_stack.append(ctx)


def pop_context():
    """
    Pop the topmost context off the stack, ending dependency tracking for the current atom.
    """
    if _context_stack:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Popping context for atom {ctx.atom_name}")
        _context_stack.pop()
    else:
        logger.warning("[DAG] Attempted to pop context, but stack was empty")
