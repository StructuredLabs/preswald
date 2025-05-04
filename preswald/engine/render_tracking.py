import ast
import contextlib
import inspect
import logging
from functools import wraps

from preswald.engine.service import PreswaldService
from preswald.interfaces.component_return import ComponentReturn
from preswald.utils import (
    generate_stable_atom_name_from_component_id,
    generate_stable_id,
)


logger = logging.getLogger(__name__)


def with_render_tracking(component_type: str):
    """
    Decorator for Preswald components that automates:
    - stable ID generation via callsite hashing
    - render-diffing using `service.should_render(...)`
    - conditional appending via `service.append_component(...)`

    It supports both wrapped (`ComponentReturn`) and raw-dict returns.

    Args:
        component_type (str): The type of the component (e.g. "text", "plot", "slider").

    Returns:
        A wrapped function that performs ID assignment and render tracking.

    Usage:
        @with_render_tracking("text")
        def text(..., component_id: str | None = None, **kwargs) -> ComponentReturn:
            ...
    """
    def decorator(func):
        # Attempt to dynamically inject **kwargs if not present
        try:
            source = inspect.getsource(func)
            tree = ast.parse(source)
            args = tree.body[0].args
            if not any(arg.arg == "kwargs" and isinstance(arg, ast.arg) for arg in args.kwonlyargs + args.args):
                original_func = func

                @wraps(func)
                def wrapped_with_kwargs(*args, **kwargs):
                    return original_func(*args, **kwargs)

                func = wrapped_with_kwargs
        except Exception as e:
            logger.warning(f"[with_render_tracking] Failed to inject kwargs {e=}")

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract a callsite hint for ID generation if not explicitly provided
            if "callsite_hint" not in kwargs:
                stack = inspect.stack()
                for frame in stack:
                    if "preswald" not in frame.filename:
                        kwargs["callsite_hint"] = f"{frame.filename}:{frame.lineno}"
                        break

            # Resolve component ID and corresponding atom name
            if "component_id" in kwargs:
                component_id = kwargs["component_id"]
                atom_name = generate_stable_atom_name_from_component_id(component_id)
                logger.debug(f"[with_render_tracking] Using provided component_id {component_id}:{atom_name}")
            else:
                identifier = kwargs.get("identifier")
                component_id = generate_stable_id(component_type, callsite_hint=kwargs["callsite_hint"], identifier=identifier)
                atom_name = generate_stable_atom_name_from_component_id(component_id)
                kwargs["component_id"] = component_id
                logger.debug(f"[with_render_tracking] Generated component_id {component_id}:{atom_name}")

            service = PreswaldService.get_instance()
            if not service.is_reactivity_enabled:
                result = func(*args, **kwargs)

                # Extract the component dict from result
                component = getattr(result, "_preswald_component", None)
                if not component and isinstance(result, dict) and "id" in result:
                    component = result

                if not component:
                    logger.warning(f"[{component_type}] No component metadata found {func.__name__=}")
                    return result

                return_value = result.value if isinstance(result, ComponentReturn) else result

                component['shouldRender'] = service.should_render(component_id, component)
                # Skip DAG logic, but still respect RenderBuffer diffing
                if service.should_render(component_id, component):
                    service.append_component(component)
                else:
                    logger.info(f"[{component_type}] Fallback: No changes detected. Skipping append {component_id=}")

                return return_value

            # Run the component function within the atom context (if not already active)
            current_atom = service._workflow._current_atom
            if current_atom:
                context = contextlib.nullcontext()
            else:
                context = service.active_atom(atom_name)

            with context:
                # Call the user-defined component function
                result = func(*args, **kwargs)

                # Extract the component dict from result
                component = getattr(result, "_preswald_component", None)
                if not component and isinstance(result, dict) and "id" in result:
                    component = result

                if not component:
                    logger.warning(f"[{component_type}] No component metadata found {func.__name__=}")
                    return result

                return_value = result.value if isinstance(result, ComponentReturn) else result

                # Register the producer for this component ID
                service._workflow.register_component_producer(component_id, atom_name)

                component['shouldRender'] = service.should_render(component_id, component)
                # Append component only if changed
                if service.should_render(component_id, component):
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[{component_type}] Created component {component=}")
                    service.append_component(component)
                else:
                    logger.info(f"[{component_type}] No changes detected. Skipping append {component_id=}")

                return return_value

        wrapper._preswald_component_type = component_type
        return wrapper

    return decorator
