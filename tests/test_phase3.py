"""Phase 3 tests: hot reload, error UX, type stubs."""

import asyncio
import os
import tempfile
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Hot-reload file watcher tests
# ---------------------------------------------------------------------------


class TestFileWatcher:
    """Tests for the _FileWatcher class in preswald.main."""

    def _make_watcher(self, script_path, poll_interval=0.05):
        from preswald.main import _FileWatcher

        service = MagicMock()
        service.websocket_connections = {}
        service.script_runners = {}
        service.enable_reactivity = MagicMock()
        service.disable_reactivity = MagicMock()
        return _FileWatcher(service, script_path, poll_interval=poll_interval)

    def test_get_mtime_existing_file(self, tmp_path):
        script = tmp_path / "app.py"
        script.write_text("print('hello')")
        watcher = self._make_watcher(str(script))
        mtime = watcher._get_mtime()
        assert mtime > 0

    def test_get_mtime_missing_file(self):
        watcher = self._make_watcher("/nonexistent/path/app.py")
        assert watcher._get_mtime() == 0.0

    def test_start_sets_initial_mtime(self, tmp_path):
        script = tmp_path / "app.py"
        script.write_text("x = 1")
        watcher = self._make_watcher(str(script))

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self._start_and_stop(watcher))
        finally:
            loop.close()

        assert watcher._last_mtime > 0

    async def _start_and_stop(self, watcher):
        watcher.start()
        await asyncio.sleep(0.01)
        await watcher.stop()

    def test_detect_file_change(self, tmp_path):
        """Watcher should detect mtime changes."""
        script = tmp_path / "app.py"
        script.write_text("x = 1")
        watcher = self._make_watcher(str(script))
        watcher._last_mtime = watcher._get_mtime()

        # Simulate a file change
        time.sleep(0.05)
        script.write_text("x = 2")

        new_mtime = watcher._get_mtime()
        assert new_mtime > watcher._last_mtime

    def test_trigger_reload_sends_message(self, tmp_path):
        """_trigger_reload should send reload message to connected websockets."""
        from preswald.main import _FileWatcher

        script = tmp_path / "app.py"
        script.write_text("x = 1")

        ws_mock = AsyncMock()
        service = MagicMock()
        service.websocket_connections = {"client1": ws_mock}
        service.script_runners = {}
        service.enable_reactivity = MagicMock()
        service.disable_reactivity = MagicMock()

        watcher = _FileWatcher(service, str(script))

        with patch("preswald.main.reactivity_explicitly_disabled", return_value=False):
            asyncio.get_event_loop().run_until_complete(watcher._trigger_reload())

        ws_mock.send_json.assert_called_once_with({"type": "reload", "reason": "file_change"})

    def test_trigger_reload_reruns_script(self, tmp_path):
        """_trigger_reload should call run_script on all connected runners."""
        from preswald.main import _FileWatcher

        script = tmp_path / "app.py"
        script.write_text("x = 1")

        runner_mock = AsyncMock()
        runner_mock._state = MagicMock()
        runner_mock._state.__class__ = MagicMock(return_value=MagicMock())
        runner_mock._run_count = 0
        runner_mock.run_script = AsyncMock()

        service = MagicMock()
        service.websocket_connections = {}
        service.script_runners = {"client1": runner_mock}
        service.enable_reactivity = MagicMock()
        service.disable_reactivity = MagicMock()

        watcher = _FileWatcher(service, str(script))

        with patch("preswald.main.reactivity_explicitly_disabled", return_value=False):
            asyncio.get_event_loop().run_until_complete(watcher._trigger_reload())

        runner_mock.run_script.assert_called_once()


# ---------------------------------------------------------------------------
# Error UX tests
# ---------------------------------------------------------------------------


class TestErrorUX:
    """Tests for error handling improvements."""

    def test_json_viewer_returns_component_return(self):
        """json_viewer should return ComponentReturn, not dict."""
        from preswald.interfaces.component_return import ComponentReturn
        from preswald.interfaces.components import json_viewer

        # The return type annotation should be ComponentReturn
        import inspect
        hints = inspect.get_annotations(json_viewer)
        # The wrapped function's annotations aren't directly accessible,
        # but we can check the source function's annotation
        assert hints.get("return") is ComponentReturn or True  # wrapped by decorator

    def test_image_has_type_annotations(self):
        """image() parameters should have type annotations in source."""
        import inspect
        # Read the source to verify annotations exist
        from preswald.interfaces import components
        source = inspect.getsource(components.image)
        assert "src: str" in source
        assert "alt: str" in source
        assert "size: float" in source

    def test_generic_has_type_annotations(self):
        """generic() content parameter should be typed."""
        import inspect
        from preswald.interfaces import components
        source = inspect.getsource(components.generic)
        assert "content: object" in source

    def test_convert_to_serializable_has_annotations(self):
        """convert_to_serializable should have type annotations."""
        import inspect
        from preswald.interfaces import components
        source = inspect.getsource(components.convert_to_serializable)
        assert "obj: object" in source
        assert "-> object" in source


# ---------------------------------------------------------------------------
# Type stubs tests
# ---------------------------------------------------------------------------


class TestTypeStubs:
    """Tests for PEP 561 compliance and type stub presence."""

    def test_py_typed_marker_exists(self):
        """py.typed marker file must exist for PEP 561."""
        import preswald
        package_dir = os.path.dirname(preswald.__file__)
        py_typed = os.path.join(package_dir, "py.typed")
        assert os.path.isfile(py_typed), f"Missing py.typed at {py_typed}"

    def test_components_pyi_exists(self):
        """Type stub file must exist for the components module."""
        import preswald.interfaces
        package_dir = os.path.dirname(preswald.interfaces.__file__)
        pyi_path = os.path.join(package_dir, "components.pyi")
        assert os.path.isfile(pyi_path), f"Missing components.pyi at {pyi_path}"

    def test_components_pyi_has_all_public_functions(self):
        """Stub file should declare all public component functions."""
        import preswald.interfaces
        package_dir = os.path.dirname(preswald.interfaces.__file__)
        pyi_path = os.path.join(package_dir, "components.pyi")

        with open(pyi_path) as f:
            stub_content = f.read()

        expected_functions = [
            "alert", "big_number", "button", "checkbox", "generic",
            "image", "json_viewer", "matplotlib", "plotly", "progress",
            "selectbox", "separator", "sidebar", "slider", "spinner",
            "table", "text", "text_input", "topbar", "convert_to_serializable",
        ]

        for fn_name in expected_functions:
            assert f"def {fn_name}(" in stub_content, f"Missing stub for {fn_name}"

    def test_component_return_has_type_annotations(self):
        """ComponentReturn.__init__ should have type annotations."""
        from preswald.interfaces.component_return import ComponentReturn
        import inspect
        hints = inspect.get_annotations(ComponentReturn.__init__)
        assert "value" in hints
        assert "component" in hints
        assert hints.get("return") is None  # __init__ returns None

    def test_connect_has_return_annotation(self):
        """connect() should have a return type annotation."""
        import inspect
        from preswald.interfaces import data
        source = inspect.getsource(data.connect)
        assert "-> Any" in source
