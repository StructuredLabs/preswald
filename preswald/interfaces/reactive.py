import inspect
import builtins
import logging
from functools import wraps, lru_cache
from types import FunctionType

from preswald.interfaces.workflow import AtomContext
from preswald.interfaces.tracked_value import TrackedValue
from preswald.interfaces.dependency_tracker import push_context, pop_context
import preswald.interfaces.components as components_module

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_builtin_components():
    """
    Return a set of Preswald component function names that should not be auto-wrapped.

    These are functions like `text`, `slider`, etc. which already have render tracking.
    """
    results = {
        name
        for name, val in vars(components_module).items()
        if callable(val) and getattr(val, "_preswald_component_type", None)
    }

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"[reactive] Builtin component names {results=}")

    return results


def reactive(func=None, *, workflow=None):
    """
    Decorator that registers a function as a reactive atom on first use.

    If called without arguments, returns a partial decorator with a workflow.
    """
    if func is None:
        return lambda actual_func: reactive(actual_func, workflow=workflow)

    @wraps(func)
    def wrapper(*args, **kwargs):
        from preswald import get_workflow

        wf = workflow or get_workflow()
        logger.info(f"[reactive] Using workflow {id(wf)=}")

        atom_name = func.__name__
        registry = wf._auto_atom_registry

        if atom_name not in registry or not hasattr(registry[atom_name], "_fresh"):
            logger.info(f"[AUTO-ATOM] Registering implicit atom {atom_name=}")
            wf._registered_reactive_atoms.append(func)

            def wrapped_body(*args, **kwargs):
                from preswald.interfaces.components import ComponentReturn

                ctx = AtomContext(workflow=wf, atom_name=atom_name)
                push_context(ctx)
                try:
                    sig = inspect.signature(func)
                    result = func(*args, **kwargs) if sig.parameters else func()

                    if isinstance(result, ComponentReturn):
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(
                                f"[reactive] Returning ComponentReturn {result.value=}, {result._preswald_component=}"
                            )
                        return result
                    elif isinstance(result, dict) and "type" in result:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(
                                f"[reactive] Returning raw component dict {result.get('value')=}, {result=}"
                            )
                        from preswald.interfaces.component_return import ComponentReturn
                        return ComponentReturn(result.get("value", None), result)

                    return TrackedValue(result, atom_name)

                finally:
                    pop_context()

            wrapped_body.__name__ = atom_name
            registered_func = wf.atom()(wrapped_body)

            # TEMPORARY: Mark this atom as freshly registered to avoid double-wrapping.
            # Once the reactive runtime is fully AST-driven, this manual marking will be unnecessary.
            registered_func._fresh = True

            registry[atom_name] = registered_func

        return registry[atom_name]

    return wrapper


def get_registered_reactive_atoms(workflow=None):
    """
    Return the list of reactive atom functions explicitly registered on the workflow.
    """
    from preswald import get_workflow
    wf = workflow or get_workflow()
    return wf._registered_reactive_atoms


def wrap_auto_atoms(globals_dict, workflow=None):
    """
    Automatically wrap zero-argument global functions as reactive atoms.

    This skips functions that are:
    - Already registered
    - Recognized as builtin Preswald components
    - Contain required positional arguments
    """
    from preswald import get_workflow

    wf = workflow or get_workflow()
    registry = wf._auto_atom_registry
    builtin_names = get_builtin_components()
    EXCLUDED_NAMES = {"wrap_auto_atoms", "reactive"}

    for name, val in globals_dict.items():
        if (
            isinstance(val, FunctionType)
            and name not in builtin_names
            and name not in registry
            and name not in EXCLUDED_NAMES
        ):
            sig = inspect.signature(val)
            has_required_params = any(
                param.default is inspect.Parameter.empty and
                param.kind in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
                for param in sig.parameters.values()
            )
            if has_required_params:
                continue

            logger.info(f"[AUTO-ATOM] Auto-wrapping global function {name=}")
            wrapped = reactive(val, workflow=wf)
            result = wrapped()
            globals_dict[name] = result

    # Force re-registration to bind wrapped atoms to workflow
    for name, wrapped in registry.items():
        wf.atom()(wrapped)


# TEMPORARY: Inject global convenience bindings.
# These will be removed once script-scoped injection is supported.
builtins.sl_reactive = reactive
builtins.sl_wrap_auto_atoms = wrap_auto_atoms
