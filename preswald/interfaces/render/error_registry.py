import os
from threading import Lock


"""
Provides a simple in-memory registry for collecting and retrieving structured
errors during different phases of script processing.

This registry is used to:
  - Accumulate multiple errors during script transformation without failing fast.
  - Provide detailed error feedback to the frontend
  - Differentiate between error types and optionally associate them with components or atoms.

All functions operate on a global in memory list with thread safety.
"""


class ErrorRegistry:
    _instance = None
    _lock = Lock()

    def __init__(self):
        self._errors_by_key = {}
        self._lock = Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _make_key(self, err: dict) -> tuple:
        return (
            err["type"],
            os.path.abspath(err["filename"]),
            err["lineno"],
            err["message"],
            err.get("atom_name"),
        )

    def register(self, **kwargs):
        with self._lock:
            key = self._make_key(kwargs)
            if key in self._errors_by_key:
                self._errors_by_key[key]["count"] += 1
            else:
                self._errors_by_key[key] = {
                    **kwargs,
                    "source": kwargs.get("source", ""),
                    "component_id": kwargs.get("component_id"),
                    "atom_name": kwargs.get("atom_name"),
                    "count": 1,
                }

    def get_errors(self, type=None, filename=None) -> list[dict]:
        with self._lock:
            return [
                e for e in self._errors_by_key.values()
                if (type is None or e["type"] == type)
                and (filename is None or os.path.samefile(e["filename"], filename))
            ]

    def clear_errors(self, type=None):
        with self._lock:
            if type:
                self._errors_by_key = {
                    k: v for k, v in self._errors_by_key.items() if v["type"] != type
                }
            else:
                self._errors_by_key.clear()


_registry = ErrorRegistry.get_instance()

def register_error(
    *,
    type: str,
    filename: str,
    lineno: int,
    message: str,
    source: str = "",
    component_id: str | None = None,
    atom_name: str | None = None,
):
    _registry.register(
        type=type,
        filename=filename,
        lineno=lineno,
        message=message,
        source=source,
        component_id=component_id,
        atom_name=atom_name,
    )

def get_errors(type: str | None = None, filename: str | None = None):
    return _registry.get_errors(type=type, filename=filename)

def clear_errors(type: str | None = None):
    _registry.clear_errors(type=type)
