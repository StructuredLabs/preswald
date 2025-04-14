import base64
import logging
import os
import shutil
import time
from typing import Any

import toml


logger = logging.getLogger(__name__)


class BrandingManager:
    """
    Manages application branding configuration and asset handling.
    This includes logo, favicon, and other customizable UI elements.
    """

    def __init__(self, static_dir: str, branding_dir: str):
        self.static_dir = static_dir
        self.branding_dir = branding_dir

    def get_branding_config(self, script_path: str | None = None) -> dict[str, Any]:
        """Get branding configuration from config file or defaults"""
        branding = {
            "name": "Preswald",
            "logo": "/images/logo.png",
            "favicon": f"/images/favicon.ico?timestamp={time.time()}",
            "primaryColor": "#000000",
        }

        if script_path:
            try:
                script_dir = os.path.dirname(script_path)
                config_path = os.path.join(script_dir, "preswald.toml")
                if os.path.exists(config_path):
                    config = toml.load(config_path)
                    logger.info(f"Loading config from {config_path}")

                    if "branding" in config:
                        branding_config = config["branding"]
                        branding["name"] = branding_config.get("name", branding["name"])
                        self._handle_logo(branding_config, script_dir, branding)
                        self._handle_favicon(branding_config, script_dir, branding)
                        branding["primaryColor"] = branding_config.get(
                            "primaryColor", branding["primaryColor"]
                        )
            except Exception as e:
                logger.error(f"Error loading branding config: {e}")
                self._ensure_default_assets()

        logger.info(f"Final branding configuration: {branding}")
        return branding

    def get_branding_config_with_data_urls(
        self, script_path: str | None = None
    ) -> dict[str, Any]:
        """Get branding config with logo and favicon as data URLs"""
        branding = self.get_branding_config(script_path)

        # Convert logo and favicon to data URLs
        branding["logo"] = self._convert_to_data_url(branding["logo"])
        branding["favicon"] = self._convert_to_data_url(
            branding["favicon"].split("?")[0]
        )  # Remove timestamp query param

        logger.info(f"Actual final branding configuration: {branding}")
        return branding

    def _convert_to_data_url(self, path: str) -> str:
        """Convert a local file path to a data URL"""
        try:
            # Check if it's already a URL or data URL
            if path.startswith(("http://", "https://", "data:")):
                return path

            # Remove leading slash if present
            if path.startswith("/"):
                path = path[1:]

            # Check in branding directory
            # local_path = os.path.join(self.branding_dir, path)
            local_path = path
            if not os.path.exists(local_path):
                logger.warning(f"File not found at {local_path}")
                return path

            # Read file and convert to base64
            with open(local_path, "rb") as f:
                data = f.read()
                b64_data = base64.b64encode(data).decode("utf-8")

            # Get MIME type from extension
            _, ext = os.path.splitext(path)
            mime_type = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".svg": "image/svg+xml",
                ".ico": "image/x-icon",
            }.get(ext.lower(), "application/octet-stream")

            return f"data:{mime_type};base64,{b64_data}"

        except Exception as e:
            logger.error(f"Error converting {path} to data URL: {e}")
            return path

    def _handle_logo(
        self, config: dict[str, Any], script_dir: str, branding: dict[str, Any]
    ):
        """Handle logo configuration and file copying"""
        if logo := config.get("logo"):
            if logo.startswith(("http://", "https://")):
                branding["logo"] = logo
                logger.info(f"Using remote logo URL: {logo}")
            else:
                logo_path = os.path.join(script_dir, logo)
                logger.info(f"Looking for logo at: {logo_path}")
                if not os.path.exists(logo_path):
                    self._copy_default_logo()
                    logger.info("Using default logo")

    def _handle_favicon(
        self, config: dict[str, Any], script_dir: str, branding: dict[str, Any]
    ):
        """Handle favicon configuration and file copying"""
        if favicon := config.get("favicon"):
            if favicon.startswith(("http://", "https://")):
                branding["favicon"] = favicon
            else:
                favicon_path = os.path.join(script_dir, favicon)
                logger.info(f"Looking for favicon at: {favicon_path}")
                if not os.path.exists(favicon_path):
                    self._copy_default_favicon()
                    logger.info("Using default favicon")

    def _ensure_default_assets(self):
        """Ensure default assets are present"""
        self._copy_default_logo()
        self._copy_default_favicon()

    def _copy_default_logo(self):
        """Copy default logo to assets directory"""
        default_logo = os.path.join(self.static_dir, "logo.png")
        if os.path.exists(default_logo):
            shutil.copy2(default_logo, os.path.join(self.branding_dir, "logo.png"))

    def _copy_default_favicon(self):
        """Copy default favicon to assets directory"""
        default_favicon = os.path.join(self.static_dir, "favicon.ico")
        if os.path.exists(default_favicon):
            shutil.copy2(
                default_favicon, os.path.join(self.branding_dir, "favicon.ico")
            )
