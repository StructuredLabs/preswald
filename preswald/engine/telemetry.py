import logging
import os
from importlib.metadata import version
from pathlib import Path
from typing import Dict, List, Optional

import requests
import tomli


STRUCTURED_CLOUD_SERVICE_URL = "http://deployer.preswald.com"
logger = logging.getLogger(__name__)


class TelemetryService:
    def __init__(self, script_path: Optional[str] = None):
        self.update_script_path(script_path)
        self.preswald_version = version("preswald")

        self._config_cache: Optional[Dict] = None
        self._last_read_time = 0
        self._telemetry_enabled = True

    def _is_telemetry_enabled(self) -> bool:
        try:
            config = self._read_config()
            telemetry_config = config.get("telemetry", {})

            if isinstance(telemetry_config, dict):
                enabled = telemetry_config.get("enabled", True)
                if isinstance(enabled, bool):
                    return enabled
                elif isinstance(enabled, str):
                    return enabled.lower() not in ("false", "off", "0", "no")

            return True
        except Exception as e:
            logger.debug(f"Error reading telemetry configuration: {e}")
            return True

    def update_script_path(self, script_path: Optional[str] = None) -> None:
        self.script_path = script_path
        if script_path:
            self.script_dir = Path(script_path).parent
            self.config_path = self.script_dir / "preswald.toml"
        else:
            self.script_dir = Path.cwd()
            self.config_path = self.script_dir / "preswald.toml"

        self._config_cache = None
        self._last_read_time = 0
        self._telemetry_enabled = self._is_telemetry_enabled()

    def _read_config(self, force: bool = False) -> Dict:
        current_time = (
            os.path.getmtime(self.config_path) if self.config_path.exists() else 0
        )

        if not force and self._config_cache and current_time <= self._last_read_time:
            return self._config_cache

        try:
            if not self.config_path.exists():
                return {}

            with open(self.config_path, "rb") as f:
                config = tomli.load(f)

            self._config_cache = config
            self._last_read_time = current_time
            return config

        except Exception:
            return {}

    def _get_project_info(self) -> Dict:
        config = self._read_config()
        project_info = config.get("project", {})

        return {
            "preswald_version": self.preswald_version,
            "preswald_slug": project_info.get("slug", "unknown"),
            "project_name": project_info.get("title", "Unknown Project"),
        }

    def _get_data_sources(self) -> List[str]:
        config = self._read_config()
        data_sources = []

        data_section = config.get("data", {})
        if data_section:
            for _, source_config in data_section.items():
                if isinstance(source_config, dict):
                    data_type = source_config.get("type")
                    if data_type:
                        data_sources.append(data_type)

        return data_sources

    def send_telemetry(
        self, event_type: str, additional_data: Optional[Dict] = None
    ) -> bool:
        if not self._telemetry_enabled:
            logger.debug("Telemetry is disabled, skipping data collection")
            return False

        try:
            telemetry_data = self._get_project_info()
            telemetry_data["data_sources"] = self._get_data_sources()
            telemetry_data["event_type"] = event_type

            if additional_data:
                telemetry_data.update(additional_data)

            response = requests.post(
                f"{STRUCTURED_CLOUD_SERVICE_URL}/telemetry",
                headers={"Content-Type": "application/json"},
                json=telemetry_data,
                timeout=5,
            )

            if response.status_code != 200:
                logger.debug(
                    f"Failed to send telemetry data: HTTP {response.status_code}"
                )

            return response.status_code == 200

        except Exception as e:
            logger.debug(f"Error sending telemetry data: {e}")
            return False

    def track_command(self, command: str, args: Optional[Dict] = None) -> bool:
        if args and "script" in args:
            script_path = args["script"]
            self.update_script_path(script_path)

        if not self._telemetry_enabled:
            logger.debug("Telemetry is disabled, skipping command tracking")
            return False

        additional_data = {"command": command, "command_args": args or {}}
        return self.send_telemetry(
            event_type="command_execution", additional_data=additional_data
        )
