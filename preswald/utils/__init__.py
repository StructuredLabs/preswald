import logging

import toml


def configure_logging(config_path=None, level=None):
    if level is None:
        level = "INFO"
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO))


def read_port_from_config(config_path="preswald.toml", port=8501):
    try:
        config = toml.load(config_path)
        return config.get("server", {}).get("port", port)
    except Exception:
        return port
