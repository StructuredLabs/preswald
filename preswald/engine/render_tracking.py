import logging
import contextlib
from functools import wraps

from preswald.engine.service import PreswaldService
from preswald.interfaces.component_return import ComponentReturn
from preswald.utils import generate_stable_id, generate_stable_atom_id_from_component_id
from preswald.engine.utils import clean_nan_values

logger = logging.getLogger(__name__)

def with_render_tracking(component_type: str, *, varname_override: dict[str, str] | None = None):
    """
    Decorator for Preswald components that automates:
    - stable ID generation via callsite hashing
    - render-diffing using `service.should_render(...)`
    - conditional appending via `service.append_component(...)`
    - DAG registration and return value storage in workflow context

    It supports both wrapped (`ComponentReturn`) and raw-dict returns.

    Args:
        component_type (str): The type of the component (e.g. "text", "plot", "slider").
        varname_override (dict[str, str] | None): Optional map from variable name to atom ID override.

    Returns:
        A wrapped function that performs ID assignment and render tracking.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            service = PreswaldService.get_instance()
            component_id = kwargs.get("component_id") or generate_stable_id(
                component_type, callsite_hint=kwargs.get("callsite_hint")
            )
            kwargs["component_id"] = component_id

            result = func(*args, **kwargs)

            component = getattr(result, "_preswald_component", None)
            if not component and isinstance(result, dict) and "id" in result:
                component = result

            if not component:
                logger.warning(f"[{component_type}] No component metadata found for tracking.")
                return result

            return_value = result.value if isinstance(result, ComponentReturn) else result

            atom_name = generate_stable_atom_id_from_component_id(component_id)
            current_atom = service._current_atom

            if current_atom and current_atom != atom_name:
                logger.warning(f"[DAG] Component {component_id} is being tracked under atom {atom_name}, "
                               f"but active atom is {current_atom}")

            with service.active_atom(atom_name):
                current_state = service.get_component_state(component_id)
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[{component_type}] Component state for {component_id} before render decision: {current_state}")

                # Explicitly register component → atom relationship
                service._workflow.register_component_producer(component_id)
                producer = service._workflow.get_component_producer(component_id)

                # Log resolution path
                if producer == atom_name:
                    logger.debug(f"[DAG] get_component_producer matched current atom: {producer}")
                elif producer:
                    logger.debug(f"[DAG] get_component_producer found distinct producer: {producer}")
                else:
                    logger.warning(f"[DAG] get_component_producer found no producer for {component_id}")

                value = component.get("value")

                if producer:
                    # apply override mappings if any
                    if varname_override:
                        for var, override in varname_override.items():
                            if override == atom_name:
                                logger.debug(f"[DAG] Overriding variable '{var}' to map to {atom_name} (was {producer})")
                                service._workflow.context.set_variable(var, value)

                    service._workflow.context.set_variable(producer, value)
                    logger.debug(f"[DAG] Stored return value of {component_id} in context under {producer}")

                    # Add reverse edge for dataflow tracking (consumer ← producer)
                    for atom in service._workflow.atoms.values():
                        if producer in atom.dependencies:
                            dag = getattr(service._workflow, "_dag", None)
                            if dag is not None:
                                dag.add_edge(producer, atom.name)

                    if producer != atom_name:
                        dag = getattr(service._workflow, "_dag", None)
                        if dag is not None:
                            dag.add_edge(atom_name, producer)
                            logger.debug(f"[DAG] Added edge: {atom_name} → {producer}")
                        else:
                            logger.warning(f"[DAG] Unable to add edge {atom_name} → {producer}, DAG not found")

                service._workflow.context.set_variable(atom_name, value)
                logger.debug(f"[DAG] Stored return value of {component_id} in context under {atom_name}")

                if producer != atom_name and component_id != atom_name:
                    service._ensure_dummy_atom(component_id)

                if service.should_render(component_id, component):
                    if current_state is not None and "value" in component:
                        component["value"] = clean_nan_values(current_state)
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"[{component_type}] Updated value from state for {component_id}: {current_state}")

                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[{component_type}] Created component: {component}")
                    service.append_component(component)
                else:
                    logger.debug(f"[{component_type}] No changes detected. Skipping append for {component_id}")

            return return_value

        wrapper._preswald_component_type = component_type
        return wrapper

    return decorator
