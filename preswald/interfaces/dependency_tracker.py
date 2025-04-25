import logging

logger = logging.getLogger(__name__)

# Thread-local context stack for dependency tracking.
# This records which atom is currently running,
# so that dynamic dependencies (like reading another atom's value)
# can be registered correctly into the DAG at runtime.
_context_stack = []

def get_current_context():
    """Return the current active dependency tracking context, if any."""
    return _context_stack[-1] if _context_stack else None

def track_dependency(dep_name: str):
    """
    Track that the current active atom depends on 'dep_name'.
    This should be called inside code paths that dynamically access other atoms.
    """
    ctx = get_current_context()
    if ctx:
        logger.debug(f"[DAG] Tracking dependency: {ctx.atom_name} → {dep_name}")
        ctx.workflow._register_dependency(ctx.atom_name, dep_name)

def push_context(ctx):
    """Push a new dependency tracking context onto the stack."""
    _context_stack.append(ctx)

def pop_context():
    """Pop the current dependency tracking context off the stack."""
    if _context_stack:
        _context_stack.pop()
    else:
        logger.warning("[DAG] Attempted to pop from empty context stack")
