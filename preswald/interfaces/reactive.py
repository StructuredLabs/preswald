import inspect
import builtins
import logging
from functools import wraps
from types import FunctionType
from preswald import get_workflow
from preswald.interfaces.workflow import AtomContext
from preswald.interfaces.components import ComponentReturn
from preswald.interfaces.tracked_value import TrackedValue
from preswald.interfaces.dependency_tracker import (
    push_context,
    pop_context,
)

logger = logging.getLogger(__name__)

# global registry to track all functions wrapped as reactive
auto_atom_registry = {}
_registered_reactive_atoms = []

# built-in component functions that should not be auto-wrapped as atoms
# TODO: dynamically populate the list of builtin components
BUILTIN_COMPONENTS = {"text", "slider", "sidebar", "chat", "plotly", "fastplotlib"}

def reactive(func=None, *, workflow=None):
    if func is None:
        return lambda actual_func: reactive(actual_func, workflow=workflow)

    _registered_reactive_atoms.append(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        wf = workflow or get_workflow()
        logger.debug(f"[reactive] using workflow id: {id(wf)}")
        atom_name = func.__name__

        if atom_name not in auto_atom_registry or not hasattr(auto_atom_registry[atom_name], "_fresh"):
            logger.debug(f"[AUTO-ATOM] Registering {atom_name} as implicit atom")

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
            auto_atom_registry[atom_name] = registered_func

        return auto_atom_registry[atom_name]()

    return wrapper

def get_registered_reactive_atoms():
    return list(_registered_reactive_atoms)

def wrap_auto_atoms(globals_dict, workflow=None):
    wf = workflow or get_workflow()

    for name, val in globals_dict.items():
        if (
            isinstance(val, FunctionType)
            and name not in auto_atom_registry
            and name not in BUILTIN_COMPONENTS
        ):
            logger.debug(f"[AUTO-ATOM] Auto-wrapping {name} at module scope")
            globals_dict[name] = reactive(val, workflow=wf)

    # reregister atoms explicitly now that all globals are wrapped
    for name, val in globals_dict.items():
        if name in auto_atom_registry:
            auto_atom_registry[name]()

# patch builtins so users don't need to import the decorator
builtins.sl_reactive = reactive
