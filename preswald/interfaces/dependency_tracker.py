import logging

logger = logging.getLogger(__name__)

# thread-local context for dependency tracking
_context_stack = []

def get_current_context():
    return _context_stack[-1] if _context_stack else None

def track_dependency(dep_name: str):
    ctx = get_current_context()
    if ctx:
        logger.debug(f"[REACTIVE] tracking dep: {dep_name}")
        ctx.workflow._register_dependency(ctx.atom_name, dep_name)

def push_context(ctx):
    _context_stack.append(ctx)

def pop_context():
    _context_stack.pop()
