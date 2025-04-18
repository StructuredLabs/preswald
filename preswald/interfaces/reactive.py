import inspect
import builtins
import logging
from functools import wraps, lru_cache
from types import FunctionType
from preswald import get_workflow
from preswald.interfaces.workflow import AtomContext
from preswald.interfaces.components import ComponentReturn
from preswald.interfaces.tracked_value import TrackedValue
from preswald.interfaces.dependency_tracker import (
    push_context,
    pop_context,
)

import preswald.interfaces.components as components_module


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_builtin_components():
    results = {
        name
        for name, val in vars(components_module).items()
        if callable(val) and getattr(val, "_preswald_component_type", None)
    }
    logger.debug(f"[get_builtin_components] builtin component names: {results}")
    return results



def reactive(func=None, *, workflow=None):
    if func is None:
        return lambda actual_func: reactive(actual_func, workflow=workflow)

    @wraps(func)
    def wrapper(*args, **kwargs):
        wf = workflow or get_workflow()
        logger.debug(f"[reactive] using workflow id: {id(wf)}")
        atom_name = func.__name__

        if not hasattr(wf, "_auto_atom_registry"):
            wf._auto_atom_registry = {}
            wf._registered_reactive_atoms = []

        registry = wf._auto_atom_registry

        if atom_name not in registry or not hasattr(registry[atom_name], "_fresh"):
            logger.debug(f"[AUTO-ATOM] Registering {atom_name} as implicit atom")
            wf._registered_reactive_atoms.append(func)

            def wrapped_body(*args, **kwargs):
                ctx = AtomContext(workflow=wf, atom_name=atom_name)
                push_context(ctx)
                try:
                    # allow dynamic args or no args depending on function signature
                    sig = inspect.signature(func)
                    if len(sig.parameters) > 0:
                        result = func(*args, **kwargs)
                    else:
                        result = func()

                    if isinstance(result, ComponentReturn):
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(
                                f"[reactive] Returning ComponentReturn: value={result.value}, component={result._preswald_component}"
                            )
                        return result
                    elif isinstance(result, dict) and "type" in result:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(
                                f"[reactive] Returning ComponentReturn: value={result.get('value')}, component={result}"
                            )
                        return ComponentReturn(result.get("value", None), result)

                    tracked = TrackedValue(result, atom_name)
                    return tracked
                finally:
                    pop_context()

            wrapped_body.__name__ = atom_name
            registered_func = wf.atom()(wrapped_body)
            registered_func._fresh = True
            registry[atom_name] = registered_func

        return registry[atom_name]()

    return wrapper

def get_registered_reactive_atoms(workflow=None):
    wf = workflow or get_workflow()
    return getattr(wf, "_registered_reactive_atoms", [])

def wrap_auto_atoms(globals_dict, workflow=None):
    wf = workflow or get_workflow()

    if not hasattr(wf, "_auto_atom_registry"):
        wf._auto_atom_registry = {}
        wf._registered_reactive_atoms = []

    registry = wf._auto_atom_registry
    builtin_names = get_builtin_components()

    for name, val in globals_dict.items():
        if (
            isinstance(val, FunctionType)
            and name not in builtin_names
            and name not in registry
        ):
            logger.debug(f"[AUTO-ATOM] Auto-wrapping {name} at module scope")
            globals_dict[name] = reactive(val, workflow=wf)

    # reregister atoms explicitly now that all globals are wrapped
    for name in registry:
        registry[name]()

# patch builtins so users don't need to import the decorator
builtins.sl_reactive = reactive
