import logging
import hashlib
import inspect
import os
import random
import re
import sys
from importlib.resources import files
from typing import Optional
from functools import wraps
from preswald.engine.service import PreswaldService

import toml

# Configure logging
logger = logging.getLogger(__name__)

def read_template(template_name):
    """Read a template file from the package."""
    template_path = files("preswald") / "templates" / f"{template_name}.template"
    return template_path.read_text()


def read_port_from_config(config_path: str, port: int):
    try:
        if os.path.exists(config_path):
            config = toml.load(config_path)
            if "project" in config and "port" in config["project"]:
                port = config["project"]["port"]
        return port
    except Exception as e:
        print(f"Warning: Could not load port config from {config_path}: {e}")


def configure_logging(config_path: str | None = None, level: str | None = None):
    """
    Configure logging globally for the application.

    Args:
        config_path: Path to preswald.toml file. If None, will look in current directory
        level: Directly specified logging level, overrides config file if provided
    """
    # Default configuration
    log_config = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    }

    # Try to load from config file
    if config_path is None:
        config_path = "preswald.toml"

    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                config = toml.load(f)
                if "logging" in config:
                    log_config.update(config["logging"])
        except Exception as e:
            print(f"Warning: Could not load logging config from {config_path}: {e}")

    # Command line argument overrides config file
    if level is not None:
        log_config["level"] = level

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_config["level"].upper()),
        format=log_config["format"],
        force=True,  # This resets any existing handlers
    )

    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.debug(f"Logging configured with level {log_config['level']}")

    return log_config["level"]


def validate_slug(slug: str) -> bool:
    pattern = r"^[a-z0-9][a-z0-9-]*[a-z0-9]$"
    return bool(re.match(pattern, slug)) and len(slug) >= 3 and len(slug) <= 63


def get_project_slug(config_path: str) -> str:
    if not os.path.exists(config_path):
        raise Exception(f"Config file not found at: {config_path}")

    try:
        config = toml.load(config_path)
        if "project" not in config:
            raise Exception("Missing [project] section in preswald.toml")

        if "slug" not in config["project"]:
            raise Exception("Missing required field 'slug' in [project] section")

        slug = config["project"]["slug"]
        if not validate_slug(slug):
            raise Exception(
                "Invalid slug format. Slug must be 3-63 characters long, "
                "contain only lowercase letters, numbers, and hyphens, "
                "and must start and end with a letter or number."
            )

        return slug

    except Exception as e:
        raise Exception(f"Error reading project slug: {e!s}") from e


def generate_slug(base_name: str) -> str:
    base_slug = re.sub(r"[^a-zA-Z0-9]+", "-", base_name.lower()).strip("-")
    random_number = random.randint(100000, 999999)
    slug = f"{base_slug}-{random_number}"
    if not validate_slug(slug):
        slug = f"preswald-{random_number}"

    return slug

def generate_stable_id(prefix: str = "component", identifier: Optional[str] = None) -> str:
    """
    Generate a stable, deterministic component ID using either:
    - a user-supplied identifier string, or
    - the source code callsite (file path and line number).

    Useful for preserving component identity across script reruns,
    supporting diff-based rerendering and caching.

    Args:
        prefix (str): A prefix for the component type (e.g., "text", "slider").
        identifier (Optional[str]): Optional string to override callsite-based ID generation.
                                    Useful when rendering multiple components from the same line
                                    or loop (e.g., in a list comprehension or for-loop).

    Returns:
        str: A stable ID like "text-abc123ef"
    """

    PRESWALD_SRC_DIR = os.path.abspath(os.path.join(__file__, ".."))

    def get_callsite_id():
        frame = inspect.currentframe()
        while frame:
            info = inspect.getframeinfo(frame)
            filepath = os.path.abspath(info.filename)

            in_preswald_src = filepath.startswith(PRESWALD_SRC_DIR)
            in_venv = ".venv" in filepath or "site-packages" in filepath
            in_stdlib = filepath.startswith(sys.base_prefix)

            if not (in_preswald_src or in_venv or in_stdlib):
                logger.info(f"[generate_stable_id] Callsite used: {filepath}:{info.lineno}")
                return f"{filepath}:{info.lineno}"

            frame = frame.f_back

        logger.warning("[generate_stable_id] Could not find valid callsite, falling back")
        return "unknown:0"

    if identifier:
        hashed = hashlib.md5(identifier.lower().encode()).hexdigest()[:8]
    else:
        callsite = get_callsite_id()
        hashed = hashlib.md5(callsite.encode()).hexdigest()[:8]

    return f"{prefix}-{hashed}"


class ComponentReturn:
    """
    Wrapper for component return values that separates the visible return
    value from the internal component metadata (e.g. for render tracking).
    """

    def __init__(self, value, component):
        self.value = value
        self._preswald_component = component

    def __str__(self): return str(self.value)
    def __float__(self): return float(self.value)
    def __bool__(self): return bool(self.value)
    def __repr__(self): return repr(self.value)


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

            # only generate ID if not explicitly passed
            component_id = kwargs.get("component_id") or generate_stable_id(component_type)
            kwargs["component_id"] = component_id

            result = func(*args, **kwargs)

            # extract the component dict
            if isinstance(result, dict) and "id" in result:
                component = result
                return_value = result
            else:
                component = getattr(result, "_preswald_component", None)
                if not component:
                    logger.warning(f"[{component_type}] No component metadata found for tracking.")
                    return result
                return_value = result.value if isinstance(result, ComponentReturn) else result

            with service.active_atom(component_id):
                if service.should_render(component_id, component):
                    logger.debug(f"[{component_type}] Created component: {component}")
                    service.append_component(component)
                else:
                    logger.debug(f"[{component_type}] No changes detected. Skipping append for {component_id}")

            return return_value
        return wrapper
    return decorator
