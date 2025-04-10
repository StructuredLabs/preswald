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
