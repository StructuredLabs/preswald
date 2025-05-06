import hashlib
import inspect
import logging
import os
import random
import re
import sys
from functools import wraps
from pathlib import Path

import toml

from preswald.engine.service import PreswaldService
from preswald.interfaces.component_return import ComponentReturn


# Configure logging
logger = logging.getLogger(__name__)

IS_PYODIDE = "pyodide" in sys.modules


def read_template(template_name, template_id=None):
    """Read a template file from the package.

    Args:
        template_name: Name of the template file without .template extension
        template_id: Optional template ID (e.g. 'executive-summary'). If not provided, uses 'default'
    """
    base_path = Path(__file__).parent / "templates"
    content = ""

    # First read from common directory
    common_path = base_path / "common" / f"{template_name}.template"
    if common_path.exists():
        content += common_path.read_text()

    # Then read from either template-specific or default directory
    template_dir = template_id if template_id else "default"
    template_path = base_path / template_dir / f"{template_name}.template"
    if template_path.exists():
        content += template_path.read_text()

    if not content:
        raise FileNotFoundError(
            f"Template {template_name} not found in common or {template_dir} directory"
        )

    return content


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


def generate_stable_id(prefix: str = "component", identifier: str | None = None) -> str:
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

    preswald_src_dir = os.path.abspath(os.path.join(__file__, ".."))

    def get_callsite_id():
        frame = inspect.currentframe()
        try:
            while frame:
                info = inspect.getframeinfo(frame)
                filepath = os.path.abspath(info.filename)

                in_preswald_src = filepath.startswith(preswald_src_dir)
                in_venv = ".venv" in filepath or "site-packages" in filepath

                # Skip stdlib check entirely if we're in pyodide
                in_stdlib = (
                    False if IS_PYODIDE else filepath.startswith(sys.base_prefix)
                )

                if not (in_preswald_src or in_venv or in_stdlib):
                    logger.debug(
                        f"[generate_stable_id] Found user code: {filepath}:{info.lineno}"
                    )
                    return f"{filepath}:{info.lineno}"

                logger.debug(
                    f"[generate_stable_id] in_preswald_src: {in_preswald_src}, in_venv: {in_venv}, in_stdlib: {in_stdlib}"
                )

                frame = frame.f_back

            return "unknown:0"
        finally:
            del frame

    if identifier:
        hashed = hashlib.md5(identifier.lower().encode()).hexdigest()[:8]
    else:
        callsite = get_callsite_id()
        hashed = hashlib.md5(callsite.encode()).hexdigest()[:8]

    return f"{prefix}-{hashed}"


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
            component_id = kwargs.get("component_id") or generate_stable_id(
                component_type
            )
            kwargs["component_id"] = component_id

            result = func(*args, **kwargs)

            # extract the component dict
            if isinstance(result, dict) and "id" in result:
                component = result
                return_value = result
            else:
                component = getattr(result, "_preswald_component", None)
                if not component:
                    logger.warning(
                        f"[{component_type}] No component metadata found for tracking."
                    )
                    return result
                return_value = (
                    result.value if isinstance(result, ComponentReturn) else result
                )

            component["shouldRender"] = service.should_render(component_id, component)

            with service.active_atom(service._workflow._current_atom):
                if service.should_render(component_id, component):
                    logger.debug(f"[{component_type}] Created component: {component}")
                    service.append_component(component)
                else:
                    logger.debug(
                        f"[{component_type}] No changes detected. Skipping append for {component_id}"
                    )

            return return_value

        return wrapper

    return decorator


def export_app_to_pdf(all_components: list[dict], output_path: str):
    """
    Export the Preswald app to PDF using fixed-size viewport.
    Waits for all passed components. Aborts if any remain unrendered.

    all_components: list of dicts like [{'id': ..., 'type': ...}, ...]
    """

    # ✅ Check all passed components (no filtering by type)
    components_to_check = [comp for comp in all_components if comp.get("id")]
    ids_to_check = [comp["id"] for comp in components_to_check]

    if not ids_to_check:
        print("⚠️ No components found to check before export.")
        return

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 3000})

        print("🌐 Connecting to Preswald app...")
        page.goto("http://localhost:8501", wait_until="networkidle")

        print(f"🔍 Waiting for {len(ids_to_check)} components to fully render...")

        try:
            # Wait until all required components are visible
            page.wait_for_function(
                """(ids) => ids.every(id => {
                    const el = document.getElementById(id);
                    return el && el.offsetWidth > 0 && el.offsetHeight > 0;
                })""",
                arg=ids_to_check,
                timeout=30000,
            )
            print("✅ All components rendered!")
        except Exception:
            # Find which ones failed to render
            missing = page.evaluate(
                """(ids) => ids.filter(id => {
                    const el = document.getElementById(id);
                    return !el || el.offsetWidth === 0 || el.offsetHeight === 0;
                })""",
                ids_to_check,
            )

            print("❌ These components did not render in time:")
            for mid in missing:
                mtype = next(
                    (c["type"] for c in components_to_check if c["id"] == mid),
                    "unknown",
                )
                print(f"  - ID: {mid}, Type: {mtype}")

            print("🛑 Aborting PDF export due to incomplete rendering.")
            browser.close()
            return

        # Ensure rendering is visually flushed
        page.evaluate(
            """() => new Promise(resolve => requestAnimationFrame(() => setTimeout(resolve, 300)))"""
        )

        # Add print-safe CSS to avoid breaking visual components across pages
        page.add_style_tag(
            content="""
            .plotly-container,
            .preswald-component,
            .component-container,
            .sidebar-desktop,
            .plotly-plot-container {
                break-inside: avoid;
                page-break-inside: avoid;
                page-break-after: auto;
                margin-bottom: 24px;
            }

            @media print {
                body {
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }
            }
        """
        )

        # Emulate screen CSS for full fidelity
        page.emulate_media(media="screen")

        # Export to PDF
        page.pdf(
            path=output_path, width="1280px", height="3000px", print_background=True
        )

        print(f"📄 PDF successfully saved to: {output_path}")
        browser.close()
