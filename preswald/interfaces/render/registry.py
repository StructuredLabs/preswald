import ast
import re
import logging
from collections import defaultdict
from typing import Callable, Any, Optional

from preswald.interfaces.component_return import ComponentReturn
from preswald.engine.transformers.frame_context import FrameContext

logger = logging.getLogger(__name__)


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
# Return-value renderers. e.g. df.to_html() returns HTML
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
# Display renderers
# ------------------------------------------------------------------------------
_display_renderers = {}
def register_display_renderer(func_name: str, renderer: Callable[[str], ComponentReturn]):
    _display_renderers[func_name] = renderer

def get_display_renderers():
    return dict(_display_renderers)

#
# special case display logic
#

def display_matplotlib_figure_show(fig, component_id: str):
    from preswald.interfaces.components import generic
    from io import BytesIO
    import base64

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode("ascii")
    data_uri = f"data:image/png;base64,{img_data}"

    return generic(data_uri, mimetype="image/png", component_id=component_id)

def display_matplotlib_show(component_id: str):
    from preswald.interfaces.components import generic
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64

    fig = plt.gcf()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode("ascii")

    # Wrap in a data URI
    data_uri = f"data:image/png;base64,{img_data}"

    # fig.savefig(buf, format="svg")
    # svg_data = buf.getvalue().decode("utf-8")
    # return generic(svg_data, mimetype="image/svg+xml", component_id=component_id)

    return generic(data_uri, mimetype="image/png", component_id=component_id)

# ------------------------------------------------------------------------------
# Dependency Resolvers
# ------------------------------------------------------------------------------
_display_dependency_resolvers = {}

def register_display_dependency_resolver(func_name: str, resolver: Callable[[FrameContext], list[str]]):
    """Register a function that determines extra dependencies for a given display call."""
    _display_dependency_resolvers[func_name] = resolver

def get_display_dependency_resolvers():
    return dict(_display_dependency_resolvers)

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
    logger.info(f'[DEBUG] pre-registring display methods')
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    import plotly.graph_objects as go

    register_display_method(go.Figure, "show")     # Plotly
    register_display_method(Figure, "show")
    register_display_renderer("matplotlib.figure.Figure.show", display_matplotlib_figure_show)


    register_display_detector(lambda call: (
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "show"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "plt"
    ))
    register_display_renderer("matplotlib.pyplot.show", display_matplotlib_show)

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
