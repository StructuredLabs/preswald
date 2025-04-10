import logging
import os
import random
import re
from importlib.resources import files
from typing import Optional

import toml
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


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


def configure_logging(config_path: Optional[str] = None, level: Optional[str] = None):
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


def export_app_to_pdf(output_path: str, port: int = 8501):
    url = f"http://localhost:{port}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 2000},
            device_scale_factor=2,
        )
        page = context.new_page()

        print(f"📄 Visiting {url} ...")
        page.goto(url, wait_until="networkidle")

        # Emulate screen media for layout fidelity
        page.emulate_media(media="screen")

        # Wait for Plotly charts to fully render
        try:
            print("⏳ Waiting for Plotly chart containers...")
            page.wait_for_selector("div.js-plotly-plot", timeout=40000)

            charts = page.query_selector_all("div.js-plotly-plot")
            for i, chart in enumerate(charts):
                print(f"🧪 Waiting for chart {i + 1} to render...")
                chart.wait_for_selector("svg", timeout=30000)

            page.wait_for_timeout(2000)  # Extra safety buffer
            print("✅ All detected charts appear rendered.")
        except PlaywrightTimeoutError:
            print("⚠️ Timeout: Some charts may not have rendered fully.")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        page.pdf(path=output_path, format="A4", print_background=True)

        print(f"✅ PDF saved to {output_path}")
        browser.close()
