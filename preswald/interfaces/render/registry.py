import ast
import base64
import importlib
import inspect
import logging
import re
from collections import defaultdict
from collections.abc import Callable
from types import ModuleType
from typing import (
    Any,
    get_args,
    get_origin,
)

import matplotlib.pyplot as plt
import plotly
from matplotlib.figure import Figure as MatplotlibFigure
from plotly.graph_objects import Figure as PlotlyFigure

from preswald.engine.transformers.frame_context import FrameContext
from preswald.interfaces.component_return import ComponentReturn


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
# return type hint registry
# ------------------------------------------------------------------------------
_return_type_hints = {}  # func_name -> str or tuple of str

def register_return_type_hint(func_name: str, return_type: str | tuple[str, ...]):
    """Register the expected return type(s) of a function or method."""
    logger.debug('[registry] register return type hint for %s -> %s', func_name, return_type)
    _return_type_hints[func_name] = return_type


def get_return_type_hint(func_name: str) -> str | tuple[str, ...] | None:
    return _return_type_hints.get(func_name)


def is_returning(func: Callable[..., Any], return_type: type[Any]) -> bool:
    try:
        sig = inspect.signature(func)
        annotation = sig.return_annotation

        if annotation is inspect.Signature.empty:
            return False

        # Direct type match
        if annotation is return_type:
            return True

        # string match, such as 'Figure'
        if isinstance(annotation, str):
            if return_type.__name__ in annotation:
                return True
            return False

        # handle generic annotations like tuple[Figure, Any]
        origin = get_origin(annotation)
        if origin is tuple:
            return any(
                arg is return_type or
                (isinstance(arg, type) and arg.__name__ == return_type.__name__)
                for arg in get_args(annotation)
            )

        return False
    except Exception:
        return False


def auto_register_return_hints(
    module: ModuleType,
    return_type: type
) -> None:
    """
    Automatically registers return type hints for all public functions in a module
    that return a specific type or include that type in a tuple return annotation.

    This utility is used to support automatic inference of reactive return values,
    such as figures produced by plotting libraries like matplotlib or plotly.

    For each matching function:
    - The fully qualified function name, such as 'plt.subplots', is used as the key.
    - The fully qualified return type name, such as 'matplotlib.figure.Figure', is used as the value.

    The check supports:
    - Direct returns: `def foo() -> Figure`
    - Tuple returns: `def bar() -> tuple[Figure, Any]`
    - String-based annotations: `-> 'Figure'`

    Args:
        module: The imported module to scan, such as `matplotlib.pyplot` or `plotly.express`.
        return_type: The target return type, such as `matplotlib.figure.Figure`, to match.

    Returns:
        None. Matching functions are registered in the return type hint registry.
    """
    full_type_name = f"{return_type.__module__}.{return_type.__name__}"

    for name, obj in vars(module).items():
        if name.startswith("_") or not callable(obj):
            continue

        if is_returning(obj, return_type):
            register_return_type_hint(f"{module.__name__}.{name}", full_type_name)

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

def get_component_type_for_function(func_name: str) -> str | None:
    return _return_renderers.get(func_name, {}).get("component_type")

def build_component_return_from_value(value: Any, mimetype: str, component_id: str) -> ComponentReturn:
    from preswald.interfaces.components import generic
    return generic(value, mimetype=mimetype, component_id=component_id)

# ------------------------------------------------------------------------------
# Display renderers
# ------------------------------------------------------------------------------
_display_renderers = {}

def register_display_renderer(
    func_name: str,
    renderer: Callable[[str], ComponentReturn],
    *,
    source_function: str | None = None,
    return_types: tuple[str, ...] | None = None
):
    """
    Register a renderer for a displayable function or method.

    Args:
        func_name: Fully qualified function name (e.g. "matplotlib.figure.Figure.show")
        renderer: Callable that takes a component_id and returns a ComponentReturn
        source_function: Optional function name (e.g. "matplotlib.pyplot.subplots") that produces the values
        return_types: Optional tuple of types returned by source_function if it returns multiple values
    """
    _display_renderers[func_name] = renderer
    if source_function and return_types:
        register_return_type_hint(source_function, return_types)
    else:
        logger.warning(f'[registry] source_function not in return_types {source_function=} {return_types=}')


def get_display_renderers():
    return dict(_display_renderers)

#
# special case display logic
#

def display_matplotlib_figure_show(fig, component_id: str):
    from io import BytesIO

    from preswald.interfaces.components import generic

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode("ascii")
    data_uri = f"data:image/png;base64,{img_data}"

    return generic(data_uri, mimetype="image/png", component_id=component_id)

def display_matplotlib_show(component_id: str):
    from io import BytesIO

    from matplotlib._pylab_helpers import Gcf

    from preswald.interfaces.components import generic

    components = []
    identifiers=[]
    # Iterate over all figure managers
    for i, manager in enumerate(Gcf.get_all_fig_managers()):
        fig = manager.canvas.figure
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode("ascii")
        data_uri = f"data:image/png;base64,{img_data}"
        html_output = f'<img src="{data_uri}" style="max-width:100%; display:block; margin-bottom:1em;" />'
        identifier = f'{component_id}_{i}'
        components.append(generic(html_output, mimetype="text/html", identifier=identifier))
        identifiers.append(identifier)

    plt.close('all')
    logger.debug(f'[DEBUG] display_matplotlib_show - returning {len(components)} with {identifiers=}')
    return tuple(components)

def display_plotly_figure_show(fig, component_id=None):
    try:

        html_bytes = fig.to_html(include_plotlyjs="cdn", full_html=True).encode("utf-8")
        data_uri = f"data:text/html;base64,{base64.b64encode(html_bytes).decode()}"
        html = f'<iframe src="{data_uri}" style="width:100%; height:500px; border:none;"></iframe>'
        return build_component_return_from_value(html, mimetype="text/html", component_id=component_id)
    except Exception as e:
        logger.exception(f"[registry] Failed to convert plotly figure to HTML: {e}")
        raise

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

def register_mimetype_component_type(mimetype: str, component_type: str | None = None):
    """
    Register a component type string to handle a given mimetype.

    If no component_type is provided, defaults to 'generic'.
    """
    if not re.match(r"^[^/]+/[^/]+$", mimetype):
        logger.warning(f"[registry] Suspicious mimetype format: {mimetype}")
    _mimetype_to_component_type[mimetype] = component_type or "generic"


def get_component_type_for_mimetype(mimetype: str) -> str | None:
    return _mimetype_to_component_type.get(mimetype)

def get_mimetype_for_function(func_name: str) -> str | None:
    return _return_renderers.get(func_name, {}).get("mimetype")

def get_mimetype_component_type_map():
    return dict(_mimetype_to_component_type)

# ------------------------------------------------------------------------------
# Plotly Submodule Discovery
# ------------------------------------------------------------------------------

def get_plotly_submodules():
    """
    Return a list of all submodules under the top level `plotly` module.

    This is used for static inspection and registration of display renderers
    or return based heuristics, such as `plotly.graph_objects.Figure.show`.

    Returns:
        A list of `ModuleType` objects representing plotly submodules.
    """
    submodules = []
    for attr in dir(plotly):
        try:
            val = getattr(plotly, attr)
            if isinstance(val, ModuleType) and val.__name__.startswith("plotly."):
                submodules.append(val)
        except Exception:
            continue
    return submodules

# ------------------------------------------------------------------------------
# Preloaded registry (can later be sourced from config)
# ------------------------------------------------------------------------------
import time  # noqa: E402


t0 = time.perf_counter()
try:
    logger.info('[DEBUG] pre-registering display methods')

    # --- Matplotlib Registration ---
    register_display_method(MatplotlibFigure, "show")

    register_display_renderer(
        f"{MatplotlibFigure.__module__}.{MatplotlibFigure.__qualname__}.show",
        display_matplotlib_figure_show,
        source_function="*",  # wild card to enable return type linkage
        return_types=(f"{MatplotlibFigure.__module__}.{MatplotlibFigure.__qualname__}",)
    )

    register_display_detector(lambda call: (
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "show"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "plt"
    ))

    register_display_renderer(
        "matplotlib.pyplot.show",
        display_matplotlib_show,
        source_function="*",
        return_types=(f"{MatplotlibFigure.__module__}.{MatplotlibFigure.__qualname__}",)
    )

    auto_register_return_hints(plt, MatplotlibFigure)

    # --- Plotly Registration ---
    register_display_method(PlotlyFigure, "show")

    full_show_name = f"{PlotlyFigure.__module__}.{PlotlyFigure.__qualname__}.show"
    return_type_str = f"{PlotlyFigure.__module__}.{PlotlyFigure.__qualname__}"

    register_display_renderer(
        full_show_name,
        display_plotly_figure_show,
        source_function="*",
        return_types=(return_type_str,)
    )

    register_display_renderer(
        "plotly.graph_objects.Figure.show",
        display_plotly_figure_show,
        source_function="*",
        return_types=("plotly.graph_objs._figure.Figure",)
    )

    # Define all known Plotly Figure types
    DEFAULT_PLOTLY_MODULES = [
        "plotly.subplots",
        "plotly.express",
        "plotly.graph_objects",
        "plotly.graph_objs"
    ]

    # Register return hints across common namespaces
    t_sub = time.perf_counter()
    modules = [importlib.import_module(mod) for mod in DEFAULT_PLOTLY_MODULES]
    for mod in modules:
        auto_register_return_hints(mod, PlotlyFigure)
    t_sub_done = time.perf_counter()
    logger.info(f"[registry] get_plotly_submodules + registration took {(t_sub_done - t_sub):.3f}s")

    # --- Mimetype registry ---
    register_mimetype_component_type("text/plain", "text")
    register_mimetype_component_type("application/json", "json_viewer")
    register_mimetype_component_type("image/png", "image")

    # --- Return renderers ---
    register_return_renderer("pandas.DataFrame.to_html", mimetype="text/html")
    register_return_renderer("pandas.DataFrame.head", mimetype="text/html")

    # --- Output stream functions ---
    register_output_stream_function("print", stream="stdout")

except ImportError:
    logger.warning("[registry] skipping pre-registration due to missing libraries")
finally:
    t1 = time.perf_counter()
    logger.info(f"[registry] full pre-registration completed in {(t1 - t0):.3f}s")

# Placeholder for user-registered return-rendering functions
# register_return_renderer("pandas.DataFrame.head", mimetype="text/html")
