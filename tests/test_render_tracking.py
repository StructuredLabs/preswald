"""Tests for preswald.engine.render_tracking.with_render_tracking decorator.

Verifies that should_render is called exactly once per component render,
covering both the non-reactive and reactive code paths.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from contextlib import nullcontext

from preswald.interfaces.component_return import ComponentReturn


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_service(*, reactivity_enabled: bool):
    """Return a mock PreswaldService with sensible defaults."""
    service = MagicMock()
    service.is_reactivity_enabled = reactivity_enabled
    service.should_render.return_value = True
    service.append_component = MagicMock()

    # Reactive-path attributes
    workflow = MagicMock()
    workflow._current_atom = None  # no atom active -> will use active_atom()
    service._workflow = workflow
    service.active_atom.return_value = nullcontext()

    return service


COMPONENT_DICT = {"id": "test-123", "type": "text", "value": "hello"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _patch_id_generators():
    """Stub out ID / atom-name generation so they return deterministic values."""
    with patch(
        "preswald.engine.render_tracking.generate_stable_id",
        return_value="test-123",
    ), patch(
        "preswald.engine.render_tracking.generate_stable_atom_name_from_component_id",
        return_value="atom_test_123",
    ):
        yield


# ---------------------------------------------------------------------------
# Non-reactive path
# ---------------------------------------------------------------------------

class TestNonReactivePath:
    """Tests for the code path where service.is_reactivity_enabled is False."""

    def test_should_render_called_exactly_once(self):
        """The bug was that should_render was invoked twice per render.
        After the fix it must be called exactly once."""
        service = _make_mock_service(reactivity_enabled=False)

        with patch(
            "preswald.engine.render_tracking.PreswaldService.get_instance",
            return_value=service,
        ):
            from preswald.engine.render_tracking import with_render_tracking

            @with_render_tracking("text")
            def my_text(component_id=None, **kwargs):
                return ComponentReturn("hello", dict(COMPONENT_DICT))

            my_text()

        service.should_render.assert_called_once()
        call_args = service.should_render.call_args
        assert call_args[0][0] == "test-123"

    def test_append_called_when_should_render_true(self):
        service = _make_mock_service(reactivity_enabled=False)
        service.should_render.return_value = True

        with patch(
            "preswald.engine.render_tracking.PreswaldService.get_instance",
            return_value=service,
        ):
            from preswald.engine.render_tracking import with_render_tracking

            @with_render_tracking("text")
            def my_text(component_id=None, **kwargs):
                return ComponentReturn("hello", dict(COMPONENT_DICT))

            my_text()

        service.append_component.assert_called_once()

    def test_append_skipped_when_should_render_false(self):
        service = _make_mock_service(reactivity_enabled=False)
        service.should_render.return_value = False

        with patch(
            "preswald.engine.render_tracking.PreswaldService.get_instance",
            return_value=service,
        ):
            from preswald.engine.render_tracking import with_render_tracking

            @with_render_tracking("text")
            def my_text(component_id=None, **kwargs):
                return ComponentReturn("hello", dict(COMPONENT_DICT))

            my_text()

        service.append_component.assert_not_called()

    def test_returns_unwrapped_value(self):
        service = _make_mock_service(reactivity_enabled=False)

        with patch(
            "preswald.engine.render_tracking.PreswaldService.get_instance",
            return_value=service,
        ):
            from preswald.engine.render_tracking import with_render_tracking

            @with_render_tracking("text")
            def my_text(component_id=None, **kwargs):
                return ComponentReturn("hello", dict(COMPONENT_DICT))

            result = my_text()

        assert result == "hello"

    def test_raw_dict_return(self):
        """Components that return a plain dict instead of ComponentReturn."""
        service = _make_mock_service(reactivity_enabled=False)

        with patch(
            "preswald.engine.render_tracking.PreswaldService.get_instance",
            return_value=service,
        ):
            from preswald.engine.render_tracking import with_render_tracking

            @with_render_tracking("text")
            def my_text(component_id=None, **kwargs):
                return {"id": "test-123", "type": "text", "value": "raw"}

            result = my_text()

        service.should_render.assert_called_once()


# ---------------------------------------------------------------------------
# Reactive path
# ---------------------------------------------------------------------------

class TestReactivePath:
    """Tests for the code path where service.is_reactivity_enabled is True."""

    def test_should_render_called_exactly_once(self):
        service = _make_mock_service(reactivity_enabled=True)

        with patch(
            "preswald.engine.render_tracking.PreswaldService.get_instance",
            return_value=service,
        ):
            from preswald.engine.render_tracking import with_render_tracking

            @with_render_tracking("text")
            def my_text(component_id=None, **kwargs):
                return ComponentReturn("hello", dict(COMPONENT_DICT))

            my_text()

        service.should_render.assert_called_once()
        call_args = service.should_render.call_args
        assert call_args[0][0] == "test-123"

    def test_registers_component_producer(self):
        service = _make_mock_service(reactivity_enabled=True)

        with patch(
            "preswald.engine.render_tracking.PreswaldService.get_instance",
            return_value=service,
        ):
            from preswald.engine.render_tracking import with_render_tracking

            @with_render_tracking("text")
            def my_text(component_id=None, **kwargs):
                return ComponentReturn("hello", dict(COMPONENT_DICT))

            my_text()

        service._workflow.register_component_producer.assert_called_once_with(
            "test-123", "atom_test_123"
        )

    def test_append_called_when_should_render_true(self):
        service = _make_mock_service(reactivity_enabled=True)
        service.should_render.return_value = True

        with patch(
            "preswald.engine.render_tracking.PreswaldService.get_instance",
            return_value=service,
        ):
            from preswald.engine.render_tracking import with_render_tracking

            @with_render_tracking("text")
            def my_text(component_id=None, **kwargs):
                return ComponentReturn("hello", dict(COMPONENT_DICT))

            my_text()

        service.append_component.assert_called_once()

    def test_append_skipped_when_should_render_false(self):
        service = _make_mock_service(reactivity_enabled=True)
        service.should_render.return_value = False

        with patch(
            "preswald.engine.render_tracking.PreswaldService.get_instance",
            return_value=service,
        ):
            from preswald.engine.render_tracking import with_render_tracking

            @with_render_tracking("text")
            def my_text(component_id=None, **kwargs):
                return ComponentReturn("hello", dict(COMPONENT_DICT))

            my_text()

        service.append_component.assert_not_called()

    def test_uses_existing_atom_context_when_active(self):
        """When _current_atom is already set, should use nullcontext."""
        service = _make_mock_service(reactivity_enabled=True)
        service._workflow._current_atom = "already_active"

        with patch(
            "preswald.engine.render_tracking.PreswaldService.get_instance",
            return_value=service,
        ):
            from preswald.engine.render_tracking import with_render_tracking

            @with_render_tracking("text")
            def my_text(component_id=None, **kwargs):
                return ComponentReturn("hello", dict(COMPONENT_DICT))

            my_text()

        # active_atom should NOT be called when an atom is already active
        service.active_atom.assert_not_called()

    def test_returns_unwrapped_value(self):
        service = _make_mock_service(reactivity_enabled=True)

        with patch(
            "preswald.engine.render_tracking.PreswaldService.get_instance",
            return_value=service,
        ):
            from preswald.engine.render_tracking import with_render_tracking

            @with_render_tracking("text")
            def my_text(component_id=None, **kwargs):
                return ComponentReturn("hello", dict(COMPONENT_DICT))

            result = my_text()

        assert result == "hello"
