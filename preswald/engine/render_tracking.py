import logging
from functools import wraps

from preswald.engine.service import PreswaldService
from preswald.interfaces.component_return import ComponentReturn
from preswald.utils import generate_stable_id


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

    Usage:
        @with_render_tracking("text")
        def text(...): ...

    Returns:
        A wrapped function that performs ID assignment and render tracking.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            service = PreswaldService.get_instance()
            component_id = kwargs.get("component_id") or generate_stable_id(component_type, callsite_hint=kwargs["callsite_hint"])
            kwargs["component_id"] = component_id

            result = func(*args, **kwargs)

            component = getattr(result, "_preswald_component", None)
            if not component and isinstance(result, dict) and "id" in result:
                component = result

            if not component:
                logger.warning(f"[{component_type}] No component metadata found for tracking.")
                return result

            return_value = result.value if isinstance(result, ComponentReturn) else result

            with service.active_atom(service._workflow._current_atom):
                if service.should_render(component_id, component):
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[{component_type}] Created component: {component}")
                    service.append_component(component)
                else:
                    logger.info(f"[{component_type}] No changes detected. Skipping append for {component_id}")

            return return_value

        wrapper._preswald_component_type = component_type
        return wrapper

    return decorator
