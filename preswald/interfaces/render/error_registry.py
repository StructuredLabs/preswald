from threading import Lock

"""
error_registry.py

Provides a simple in-memory registry for collecting and retrieving structured
errors during different phases of script processing.

This registry is used to:
  - Accumulate multiple errors during script transformation without failing fast.
  - Provide detailed error feedback to the frontend
  - Differentiate between error types and optionally associate them with components or atoms.

All functions operate on a global in memory list with thread safety.
"""

# Global in-memory registry and associated lock
_error_registry = []
_registry_lock = Lock()

def register_error(
    *,
    type: str,             # examples: "ast_transform", "runtime", "render"
    filename: str,         # Filename or script path associated with the error
    lineno: int,           # Line number where the error occurred
    message: str,          # Error message
    source: str = "",      # Source code snippet or context
    component_id: str | None = None,  # Optional component ID if error is linked to a specific component
    atom_name: str | None = None      # Optional atom name if error is linked to a reactive atom
):
    """
    Register a new structured error.

    Args:
        type: A string categorizing the error, such as "ast_transform", "runtime".
        filename: The script or file in which the error occurred.
        lineno: The line number where the error was detected.
        message: A human-readable description of the error.
        source: Optional source code excerpt or context around the error.
        component_id: Optional ID of the UI component associated with this error.
        atom_name: Optional name of the reactive atom associated with this error.
    """
    with _registry_lock:
        _error_registry.append({
            "type": type,
            "filename": filename,
            "lineno": lineno,
            "message": message,
            "source": source,
            "component_id": component_id,
            "atom_name": atom_name,
        })

def get_errors(type: str | None = None, filename: str | None = None):
    """
    Retrieve all registered errors, optionally filtered by type and/or filename.

    Args:
        type: Optional error type to filter by, such as "ast_transform".
        filename: Optional filename to filter by.

    Returns:
        A list of matching error dicts.
    """
    with _registry_lock:
        return [
            err for err in _error_registry
            if (type is None or err["type"] == type)
            and (filename is None or err["filename"] == filename)
        ]

def clear_errors(type: str | None = None):
    """
    Clear errors from the registry.

    Args:
        type: Optional type of errors to clear. If omitted, all errors are removed.
    """
    global _error_registry
    with _registry_lock:
        if type:
            _error_registry = [e for e in _error_registry if e["type"] != type]
        else:
            _error_registry = []
