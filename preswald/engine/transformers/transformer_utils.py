import ast
import logging
import collections.abc
from typing import Any

from preswald.interfaces.component_return import ComponentReturn
from preswald.utils import (
    generate_stable_id,
)


logger = logging.getLogger(__name__)


def get_call_func_name(call_node: ast.Call) -> str | None:
    """
    Extract the function name from an AST call node.

    This utility handles both direct function calls like `slider(...)`
    and attribute based calls like `preswald.slider(...)`.

    Args:
        call_node: An `ast.Call` node representing a function invocation.

    Returns:
        The name of the function being called, or None if it cannot be
        determined.
    """
    if isinstance(call_node.func, ast.Name):
        return call_node.func.id
    elif isinstance(call_node.func, ast.Attribute):
        return call_node.func.attr
    return None

def extract_call_args(call_node: ast.Call) -> tuple[list[Any], dict[str, Any]]:
    """
    Extract positional and keyword arguments from an AST call node.

    This function attempts to statically extract values from `ast.Call` nodes
    for common literal types like constants and f-strings. Non literal values
    are returned as AST dumps for diagnostic or fallback purposes.

    Args:
        call_node: An `ast.Call` node representing a function invocation.

    Returns:
        A tuple containing:
            - A list of extracted positional arguments.
            - A dictionary of extracted keyword arguments.
    """
    args = []
    kwargs = {}
    for arg in call_node.args:
        if isinstance(arg, ast.Constant):
            args.append(arg.value)
        elif isinstance(arg, ast.JoinedStr):
            # fallback to unparsed string representation
            args.append(ast.unparse(arg).strip())
        else:
            args.append(ast.dump(arg))  # or handle other node types more gracefully

    for kw in call_node.keywords:
        if isinstance(kw.value, ast.Constant):
            kwargs[kw.arg] = kw.value.value
        elif isinstance(kw.value, ast.JoinedStr):
            kwargs[kw.arg] = ast.unparse(kw.value).strip()
        else:
            kwargs[kw.arg] = ast.dump(kw.value)

    return args, kwargs


def build_component_from_args(name: str, args: list, kwargs: dict) -> ComponentReturn:
    """
    Reconstruct a Preswald component by invoking its registered constructor.

    This function is used to rebuild a component from a known function name,
    positional arguments, and keyword arguments. It is typically called during
    runtime error recovery or fallback rendering when the original component
    failed to compute.

    Only components defined in `preswald.interfaces.components` and marked with
    the `_preswald_component_type` attribute are considered valid. The function
    must return a `ComponentReturn`, which encapsulates both the visible value
    and the component metadata.

    If reconstruction fails at any point, the function is not a valid component,
    or the return type is incorrect, a fallback error component is returned instead.

    Args:
        name: Name of the component function
        args: Positional arguments for the component constructor
        kwargs: Keyword arguments for the component constructor

    Returns:
        ComponentReturn: A fully constructed component if successful,
                         or a fallback error component otherwise.
    """
    from preswald.interfaces import components

    try:
        fn = getattr(components, name, None)
        if fn is None or not callable(fn):
            raise ValueError(f"No component function found with name '{name}'")

        _preswald_component_type = getattr(fn, "_preswald_component_type", None)
        if _preswald_component_type is None:
            raise ValueError(f"Name matched function that is not a preswald component type: '{name=}'")

        result = fn(*args, **kwargs)

        if not isinstance(result, ComponentReturn):
            raise ValueError(f"The Result of named function is not a ComponentReturn type: '{name=}'")

        return result

    except Exception as e:
        component_id = kwargs.get('component_id', None)
        if not component_id:
            component_id = generate_stable_id(prefix=name, callsite_hint=callsite_hint)
        component = {
            "id": component_id,
            "type": name,
            "error": f"[Rebuild Error] {e!s}"
        }
        component.update(_filter_kwargs_for_fallback(kwargs))
        return ComponentReturn(None, component)


def rebuild_component_from_source(
    lifted_component_src: str,
    callsite_hint: str,
    *,
    force_render: bool=False
) -> ComponentReturn:
    """
    Reconstruct a Preswald component from its lifted AST call expression.

    This function is primarily used during runtime error recovery to reconstruct
    a component from source code that was previously extracted and stored from the
    original callsite. It parses the expression, extracts its arguments, and invokes
    the appropriate Preswald component function.

    The reconstructed component is wrapped in a `ComponentReturn` and can be safely
    sent to the frontend, even when the original component computation failed.

    Render tracking is temporarily suppressed during reconstruction to avoid duplicate
    layout registration or state interference.

    Args:
        lifted_component_src: Source code string of the original component call expression.
        callsite_hint: A 'filename:lineno' style hint used to generate a stable component ID.

    Keyword Args:
        force_render: If True, the returned component will include `'shouldRender': True`.

    Returns:
        ComponentReturn: The reconstructed component wrapped in a `ComponentReturn` object.

    Raises:
        ValueError: If the source is not a valid single call expression.
        Exception: If component reconstruction fails for any reason.
    """
    expr_module = ast.parse(lifted_component_src, mode="exec")
    if (
        len(expr_module.body) == 1 and
        isinstance(expr_module.body[0], ast.Expr) and
        isinstance(expr_module.body[0].value, ast.Call)
    ):
        expr_ast = expr_module.body[0].value
        name = get_call_func_name(expr_ast)
        args, kwargs = extract_call_args(expr_ast)

        kwargs["component_id"] = generate_stable_id(prefix=name, callsite_hint=callsite_hint)

        from preswald.engine.service import PreswaldService

        service = PreswaldService.get_instance()
        with service.render_tracking_suppressed():
            component_return = build_component_from_args(name, args, kwargs)
        if force_render:
            component_return.component['shouldRender'] = True

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"[transform_utils.rebuild_component_from_source] Reconstructed component: {component_return=}")
        return component_return

    raise ValueError("Invalid lifted_component_src: unable to parse call expression.")

def _safe_for_fallback(value):
    return isinstance(value, (str, int, float, bool, type(None)))

def _filter_kwargs_for_fallback(kwargs):
    return {k: v for k, v in kwargs.items() if isinstance(k, str) and _safe_for_fallback(v)}
