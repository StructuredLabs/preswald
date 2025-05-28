import re
from collections import defaultdict
from typing import Callable, Any, Optional

from preswald.interfaces.component_return import ComponentReturn

# ------------------------------------------------------------------------------
# Stream-based output registry. e.g. print
# ------------------------------------------------------------------------------
_output_stream_calls = {}  # func name -> stream identifier, e.g. "stdout"

def register_output_stream_function(func_name: str, stream: str):
    """Register a function that produces output via a stream."""
    _output_stream_calls[func_name] = stream

def get_output_stream_calls():
    return dict(_output_stream_calls)

# ------------------------------------------------------------------------------
# Method-based output registry. e.g. fig.show
# ------------------------------------------------------------------------------
_display_methods = defaultdict(set)

def register_display_method(cls: type, method_name: str):
    """Register a method name for a given class that should trigger auto-display."""
    _display_methods[cls].add(method_name)

def get_display_methods():
    return dict(_display_methods)

# ------------------------------------------------------------------------------
# AST-based call detectors. e.g. render_function_identity("print")
# ------------------------------------------------------------------------------
_display_detectors = []

def register_display_detector(fn: Callable[[Any], bool]):
    """Register a callable that takes an ast.Call and returns True if it should be auto-rendered."""
    _display_detectors.append(fn)

def get_display_detectors():
    return list(_display_detectors)

# ------------------------------------------------------------------------------
# Return-value renderers. e.g. df.head() returns HTML
# ------------------------------------------------------------------------------
_return_renderers = {}  # func name -> { "mimetype": str, "component_type": Optional[str] }

def register_return_renderer(func_name: str, *, mimetype: str, component_type: str | None = None):
    """
    Register a function that returns a renderable value.

    Args:
        func_name: Fully qualified function name (e.g. "pandas.DataFrame.head")
        mimetype: MIME type of the returned content (e.g. "text/html")
        component_type: Optional override for which component to use. If not provided,
                        defaults to the registered component for that mimetype.
    """

    # Use the registered component type unless explicitly overridden
    final_component_type = component_type or get_component_type_for_mimetype(mimetype)

    if not final_component_type:
        logger.warning(f"[register_return_renderer] No component registered for {mimetype=}. Using fallback.")

    _return_renderers[func_name] = {
        "mimetype": mimetype,
        "component_type": final_component_type,
    }


def get_return_renderers():
    return dict(_return_renderers)

def get_component_type_for_function(func_name: str) -> Optional[str]:
    return _return_renderers.get(func_name, {}).get("component_type")

def build_component_return_from_value(value: Any, mimetype: str, component_id: str) -> ComponentReturn:
    from preswald.interfaces.components import generic
    return generic(value, mimetype=mimetype, component_id=component_id)

# ------------------------------------------------------------------------------
# Mimetype-to-widget registry (generic dispatch)
# ------------------------------------------------------------------------------
_mimetype_to_component_type = {}

def register_mimetype_component_type(mimetype: str, component_type: Optional[str] = None):
    """
    Register a component type string to handle a given mimetype.

    If no component_type is provided, defaults to 'generic'.
    """
    if not re.match(r"^[^/]+/[^/]+$", mimetype):
        logger.warning(f"[registry] Suspicious mimetype format: {mimetype}")
    _mimetype_to_component_type[mimetype] = component_type or "generic"


def get_component_type_for_mimetype(mimetype: str) -> Optional[str]:
    return _mimetype_to_component_type.get(mimetype)

def get_mimetype_for_function(func_name: str) -> Optional[str]:
    return _return_renderers.get(func_name, {}).get("mimetype")

def get_mimetype_component_type_map():
    return dict(_mimetype_to_component_type)

# ------------------------------------------------------------------------------
# Preloaded registry (can later be sourced from config)
# ------------------------------------------------------------------------------
try:
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go

    register_display_method(go.Figure, "show")     # Plotly
    register_display_method(plt.Figure, "show")    # Matplotlib object
    register_display_method(plt, "show")           # pyplot.show()

    register_output_stream_function("print", stream="stdout")

    # Register basic mimetype renderers
    register_mimetype_component_type("text/plain", "text")  # maps to MarkdownRendererWidget
    register_mimetype_component_type("text/html", "text")   # maps to MarkdownRendererWidget
    register_mimetype_component_type("application/json", "json_viewer")
    register_mimetype_component_type("image/png", "image")
except ImportError:
    pass  # Skip preload if dependencies aren't installed

# Placeholder for user-registered return-rendering functions
# register_return_renderer("pandas.DataFrame.head", mimetype="text/html")
