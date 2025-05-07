import hashlib
import inspect
import logging
import os
import random
import re
import sys
from pathlib import Path

import toml


# Configure logging
logger = logging.getLogger(__name__)

IS_PYODIDE = "pyodide" in sys.modules

def read_disable_reactivity(config_path: str) -> bool:
    """
    Read the --disable-reactivity flag from the TOML config.

    Args:
        config_path: Path to preswald.toml

    Returns:
        bool: True if reactivity should be disabled
    """
    try:
        if os.path.exists(config_path):
            config = toml.load(config_path)
            return bool(config.get("project", {}).get("disable_reactivity", False))
    except Exception as e:
        logger.warning(f"Could not load disable_reactivity from {config_path}: {e}")
    return False

def reactivity_explicitly_disabled(config_path: str = "preswald.toml") -> bool:
    """Check if reactivity is disabled in project configuration."""
    try:
        return read_disable_reactivity(config_path)
    except Exception as e:
        logger.warning(f"[is_app_reactivity_disabled] Failed to read config: {e}")
        return False

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


def generate_stable_id(
    prefix: str = "component",
    identifier: str | None = None,
    callsite_hint: str | None = None,
) -> str:
    """
    Generate a stable, deterministic component ID using:
    - a user-supplied identifier string, or
    - the source code callsite (file path and line number).

    Args:
        prefix (str): Prefix for the component type (e.g., "text", "slider").
        identifier (Optional[str]): Overrides callsite-based ID generation.
        callsite_hint (Optional[str]): Explicit callsite (e.g., "file.py:42") for deterministic hashing.

    Returns:
        str: A stable component ID like "text-abc123ef".
    """
    if identifier:
        hashed = hashlib.md5(identifier.lower().encode()).hexdigest()[:8]
        logger.debug(f"[generate_stable_id] Using provided identifier to generate hash {hashed=}")
        return f"{prefix}-{hashed}"

    fallback_callsite = "unknown:0"

    if callsite_hint:
        if ":" in callsite_hint:
            filename, lineno = callsite_hint.rsplit(":", 1)
            try:
                int(lineno)  # Validate it's a number
                callsite_hint = f"{filename}:{lineno}"
            except ValueError:
                logger.warning(f"[generate_stable_id] Invalid line number in callsite_hint {callsite_hint=}")
                callsite_hint = None
        else:
            logger.warning(f"[generate_stable_id] Invalid callsite_hint format (missing colon) {callsite_hint=}")
            callsite_hint = None

    if not callsite_hint:
        preswald_src_dir = os.path.abspath(os.path.join(__file__, ".."))

        def get_callsite_id():
            frame = inspect.currentframe()
            try:
                while frame:
                    info = inspect.getframeinfo(frame)
                    filepath = os.path.abspath(info.filename)

                    if IS_PYODIDE:
                        # In Pyodide: skip anything in /lib/, allow /main.py etc.
                        if not filepath.startswith("/lib/"):
                            logger.debug(f"[generate_stable_id] [Pyodide] Found user code: {filepath}:{info.lineno}")
                            return f"{filepath}:{info.lineno}"
                    else:
                        # In native: skip stdlib, site-packages, and preswald internals
                        in_preswald_src = filepath.startswith(preswald_src_dir)
                        in_venv = ".venv" in filepath or "site-packages" in filepath
                        in_stdlib = filepath.startswith(sys.base_prefix)

                        if not (in_preswald_src or in_venv or in_stdlib):
                            logger.debug(f"[generate_stable_id] Found user code: {filepath}:{info.lineno}")
                            return f"{filepath}:{info.lineno}"

                    frame = frame.f_back

                logger.warning("[generate_stable_id] No valid callsite found, falling back to default")
                return fallback_callsite
            finally:
                del frame

        callsite_hint = get_callsite_id()

    hashed = hashlib.md5(callsite_hint.encode()).hexdigest()[:8]
    logger.debug(f"[generate_stable_id] Using final callsite_hint to generate hash {hashed=} {callsite_hint=}")
    return f"{prefix}-{hashed}"


def generate_stable_atom_name_from_component_id(component_id: str, prefix: str = "_auto_atom") -> str:
    """
    Convert a stable component ID into a corresponding atom name.
    Normalizes the suffix and replaces hyphens with underscores.

    Example:
        component_id='text-abc123ef' → '_auto_atom_abc123ef'

    Args:
        component_id (str): A previously generated component ID.
        prefix (str): Optional prefix for the atom name.

    Returns:
        str: A deterministic, underscore-safe atom name.
    """
    if component_id and "-" in component_id:
        hash_part = component_id.rsplit("-", 1)[-1]
        return f"{prefix}_{hash_part}"

    logger.warning(f"[generate_stable_atom_name_from_component_id] Unexpected component_id format {component_id=}")
    return generate_stable_id(prefix)


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
