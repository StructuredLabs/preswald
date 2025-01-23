import logging
import toml
import os
import pkg_resources
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def read_template(template_name):
    """Read content from a template file."""
    template_path = pkg_resources.resource_filename(
        "preswald", f"templates/{template_name}.template"
    )
    with open(template_path, "r") as f:
        return f.read()


def configure_logging(config_path: Optional[str] = None, level: Optional[str] = None):
    """
    Configure logging globally for the application.

    Args:
        config_path: Path to config.toml file. If None, will look in current directory
        level: Directly specified logging level, overrides config file if provided
    """
    # Default configuration
    log_config = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    }

    # Try to load from config file
    if config_path is None:
        config_path = "config.toml"

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
