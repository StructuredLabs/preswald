import hashlib
import inspect
import logging
import os
import random
import re
import sys
import toml

from importlib.resources import files as importlib_files


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


def get_user_code_callsite(exc: BaseException | None = None, fallback: str = "unknown:0") -> tuple[str, int]:
    """
    Attempts to find the callsite of user code.

    If an exception is provided, uses its traceback to find the origin of the error.
    Otherwise, falls back to inspecting the current frame.

    Returns:
        A tuple (filename, lineno) pointing to the first user code location.
    """
    preswald_src_dir = os.path.abspath(os.path.join(__file__, ".."))

    def is_user_code(filepath: str) -> bool:
        filepath = os.path.abspath(filepath)
        return not (
            filepath.startswith(preswald_src_dir)
            or filepath.startswith(sys.prefix)
            or filepath.startswith(sys.base_prefix)
            or "site-packages" in filepath
        )

    if exc and exc.__traceback__:
        tb = exc.__traceback__
        while tb:
            filename = os.path.abspath(tb.tb_frame.f_code.co_filename)
            lineno = tb.tb_lineno
            if is_user_code(filename):
                return filename, lineno
            tb = tb.tb_next

    frame = inspect.currentframe()
    try:
        while frame:
            info = inspect.getframeinfo(frame)
            filepath = os.path.abspath(info.filename)

            if "pyodide" in sys.modules:
                if not filepath.startswith("/lib/"):
                    return filepath, info.lineno
            elif is_user_code(filepath):
                return filepath, info.lineno

            frame = frame.f_back

    finally:
        del frame

    return fallback, 0


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
        hashed = hashlib.md5(identifier.lower().encode()).hexdigest()[:12]
        logger.debug(
            f"[generate_stable_id] Using provided identifier to generate hash {hashed=}"
        )
        return f"{prefix}-{hashed}"

    fallback_callsite = "unknown:0"

    if callsite_hint:
        if ":" in callsite_hint:
            filename, lineno = callsite_hint.rsplit(":", 1)
            try:
                int(lineno)  # Validate it's a number
                callsite_hint = f"{filename}:{lineno}"
            except ValueError:
                logger.warning(
                    f"[generate_stable_id] Invalid line number in callsite_hint {callsite_hint=}"
                )
                callsite_hint = None
        else:
            logger.warning(
                f"[generate_stable_id] Invalid callsite_hint format (missing colon) {callsite_hint=}"
            )
            callsite_hint = None

    if not callsite_hint:
        filepath, lineno = get_user_code_callsite()
        callsite_hint = f"{filepath}:{lineno}"

    hashed = hashlib.md5(callsite_hint.encode()).hexdigest()[:12]

    logger.debug(
        f"[generate_stable_id] Using final callsite_hint to generate hash {hashed=} {callsite_hint=}"
    )
    return f"{prefix}-{hashed}"


def generate_stable_atom_name_from_component_id(
    component_id: str, prefix: str = "_auto_atom"
) -> str:
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

    logger.warning(
        f"[generate_stable_atom_name_from_component_id] Unexpected component_id format {component_id=}"
    )
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


def get_boot_script_html(client_type="auto"):
    """
    Read the boot script template and wrap it in proper HTML script tags.
    Returns a tuple of (head_script, body_script) to be injected into index.html.

    Args:
        client_type (str): The client type to use ("auto", "websocket", "postmessage", "comlink")
    """
    try:
        template_path = importlib_files("preswald").joinpath("browser/boot.js")
        with template_path.open("r") as f:
            boot_js = f.read()

        head_script = f"""
    <script>
    window.__PRESWALD_CLIENT_TYPE = "{client_type}";
    </script>
</head>"""

        body_script = f"""
    <script type="module">
    {boot_js}
    </script>
  </body>
</html>"""

        return head_script, body_script

    except Exception as e:
        logger.error(f"Failed to read boot script template: {e}")
        raise


def serialize_fs(root_dir=".", output_dir=None):
    """Walk directory and create file entries for project_fs.json

    Args:
        root_dir (str): The directory to start walking from
        output_dir (str, optional): Directory to exclude from the snapshot

    Returns:
        dict: A dictionary mapping file paths to their contents
    """
    import base64

    result = {}
    for root, _dirs, files in os.walk(root_dir):
        if output_dir:
            abs_output = os.path.abspath(output_dir)
            abs_root = os.path.abspath(root)

            if abs_root == abs_output or abs_root.startswith(abs_output + os.sep):
                continue

        for file in files:
            if file.startswith("."):
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, root_dir)

            try:
                with open(full_path) as f:
                    content = f.read()
                result[rel_path] = {"type": "text", "content": content}
            except UnicodeDecodeError:
                with open(full_path, "rb") as f:
                    binary_content = f.read()
                encoded = base64.b64encode(binary_content).decode("ascii")
                result[rel_path] = {"type": "binary", "content": encoded}

    return result


def prepare_html_export(
    script_path: str,
    output_dir: str,
    project_root_dir: str,
    client_type: str = "comlink",
):
    """
    Prepares all necessary files for an HTML export in the specified output_dir.

    Args:
        script_path (str): Absolute path to the main Preswald script (e.g., /project/app.py or /path/to/user/app.py).
        output_dir (str): The directory where all export files will be staged.
        project_root_dir (str): The root directory of the project files (e.g., \".\" for CLI, \"/project\" for Pyodide).
        client_type (str): The client communication type.
    """
    import json
    import shutil
    import time
    from importlib.resources import as_file
    from importlib.resources import files as pkg_files

    from preswald.engine.managers.branding import BrandingManager

    logger.info(
        f"Preparing HTML export for '{script_path}' into '{output_dir}' with project root '{project_root_dir}'"
    )

    os.makedirs(output_dir, exist_ok=True)

    # 1. Create project_fs.json
    logger.info("Creating project filesystem snapshot...")
    fs_snapshot = serialize_fs(root_dir=project_root_dir, output_dir=output_dir)

    # The entrypoint in project_fs.json should be relative to project_root_dir
    # If script_path is /project/app.py and project_root_dir is /project, entrypoint is app.py
    # If script_path is /Users/foo/proj/app.py and project_root_dir is ., entrypoint is app.py (assuming script is in root)
    # More robustly, make script_path relative to project_root_dir
    if os.path.isabs(script_path) and os.path.isabs(project_root_dir):
        # Both absolute, make script_path relative to project_root_dir
        entrypoint_rel_path = os.path.relpath(script_path, project_root_dir)
    elif not os.path.isabs(script_path) and not os.path.isabs(project_root_dir):
        # Both relative (e.g. script_path='app.py', project_root_dir='.')
        # This case is typical for CLI where cwd is project_root_dir
        entrypoint_rel_path = script_path
    else:
        # Mixed cases, or script_path is already relative as intended.
        # Default to basename if unsure, but this might be incorrect if script is in a subfolder.
        logger.warning(
            f"Ambiguous paths for entrypoint determination: script_path='{script_path}', project_root_dir='{project_root_dir}'. Using basename."
        )
        entrypoint_rel_path = os.path.basename(script_path)

    fs_snapshot["__entrypoint__"] = entrypoint_rel_path
    project_fs_json_path = os.path.join(output_dir, "project_fs.json")
    with open(project_fs_json_path, "w") as f:
        json.dump(fs_snapshot, f)
    logger.info(f"Project filesystem snapshot saved to {project_fs_json_path}")

    # 2. Copy static files from preswald installation
    preswald_pkg_static_path = pkg_files("preswald") / "static"

    # Copy index.html
    dest_index_html = os.path.join(output_dir, "index.html")
    with as_file(preswald_pkg_static_path / "index.html") as src_index_path:
        shutil.copy2(src_index_path, dest_index_html)

    # Copy assets directory
    dest_assets_dir = os.path.join(output_dir, "assets")
    if os.path.exists(dest_assets_dir):
        shutil.rmtree(dest_assets_dir)
    with as_file(preswald_pkg_static_path / "assets") as src_assets_path:
        shutil.copytree(src_assets_path, dest_assets_dir)
    logger.info(f"Copied Preswald static assets to {output_dir}")

    # 3. Modify index.html (add branding, boot script)
    head_script, body_script = get_boot_script_html(
        client_type=client_type
    )

    # Initialize branding manager
    # For BrandingManager, static_dir is the path to package's static files (e.g., .../preswald/static)
    # branding_dir is the path to user's images (e.g. /project/images or ./images)
    user_images_dir_name = "images"  # Standard name for user's branding images
    user_branding_images_path = os.path.join(project_root_dir, user_images_dir_name)

    # BrandingManager needs string paths
    branding_manager = BrandingManager(
        str(preswald_pkg_static_path), user_branding_images_path
    )

    # Get branding configuration. script_path should be the original script path.
    # BrandingManager's get_branding_config_with_data_urls internally uses os.path.dirname(script_path)
    # to find preswald.toml. So script_path needs to be the actual path to the script.
    branding = branding_manager.get_branding_config_with_data_urls(script_path)

    with open(dest_index_html, "r+") as f:
        index_content = f.read()
        # Replace title
        index_content = index_content.replace(
            "<title>Vite + React</title>", f"<title>{branding['name']}</title>"
        )
        # Add favicon links
        favicon_links = f'''<link rel="icon" type="image/x-icon" href="{branding["favicon"]}" />
    <link rel="shortcut icon" type="image/x-icon" href="{branding["favicon"]}?timestamp={time.time()}" />'''
        # Remove existing favicon link(s) more robustly
        index_content = re.sub(
            r'<link[^>]*rel=["\\\'](shortcut )?icon["\\\'][^>]*>',
            "",
            index_content,
            flags=re.IGNORECASE,
        )

        # Add new favicon links. Try to place it after <meta charset...>, or after <head>
        meta_charset_tag = '<meta charset="UTF-8" />'
        if meta_charset_tag in index_content:
            index_content = index_content.replace(
                meta_charset_tag, f"{meta_charset_tag}\n{favicon_links}"
            )
        elif "<head>" in index_content:
            index_content = index_content.replace("<head>", f"<head>\n{favicon_links}")
        else:  # Fallback if head or charset not found
            index_content = favicon_links + "\n" + index_content

        # Add branding data and boot script
        branding_script_tag = (
            f"<script>window.PRESWALD_BRANDING = {json.dumps(branding)};</script>"
        )
        scripts_to_inject = f"{branding_script_tag}\n{head_script}"

        if "</head>" in index_content:
            index_content = index_content.replace(
                "</head>", f"{scripts_to_inject}\n</head>"
            )
        else:  # Fallback if </head> not found
            index_content = index_content + "\n" + scripts_to_inject

        # Add the boot script to the body (before </body>)
        if "</body>" in index_content:
            # Extract just the script tag from body_script (remove </body></html>)
            boot_script_tag = body_script.split("</body>")[0].strip()
            index_content = index_content.replace(
                "</body>", f"{boot_script_tag}\n</body>"
            )
        else:  # Fallback if </body> not found
            # Extract just the script tag from body_script
            boot_script_tag = body_script.split("</body>")[0].strip()
            index_content = index_content + "\n" + boot_script_tag

        f.seek(0)
        f.write(index_content)
        f.truncate()
    logger.info(f"Modified index.html in {output_dir} with branding and boot scripts.")
    logger.info(f"HTML export preparation complete in {output_dir}")
