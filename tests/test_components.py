"""Tests for the Preswald component protocol.

Verifies that every component function returns a value whose associated
component dict contains at least {"type": <str>, "id": <str>}, plus any
component-specific fields.
"""

import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_preswald_service():
    """Mock PreswaldService.get_instance() for all tests.

    The render_tracking decorator and stateful components (button, checkbox,
    selectbox, slider, text_input) call PreswaldService.get_instance().
    """
    mock_service = MagicMock()
    mock_service.get_component_state.return_value = None
    mock_service.is_reactivity_enabled = False
    mock_service.should_render.return_value = True
    mock_service.append_component.return_value = None

    with patch("preswald.engine.render_tracking.PreswaldService") as rt_cls, \
         patch("preswald.interfaces.components.PreswaldService") as comp_cls:
        rt_cls.get_instance.return_value = mock_service
        comp_cls.get_instance.return_value = mock_service
        yield mock_service


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_component(mock_service, call_index=-1):
    """Extract the component dict that was passed to append_component."""
    return mock_service.append_component.call_args_list[call_index][0][0]


def _assert_base(component, expected_type, expected_id="test-id"):
    """Assert the minimal component protocol fields."""
    assert isinstance(component, dict)
    assert isinstance(component["type"], str)
    assert component["type"] == expected_type
    assert isinstance(component["id"], str)
    assert component["id"] == expected_id


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAlert:
    def test_returns_value(self, mock_preswald_service):
        from preswald.interfaces.components import alert
        result = alert("Watch out!", level="warning", size=0.5, component_id="test-id")
        assert result == "Watch out!"

    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import alert
        alert("Watch out!", level="warning", size=0.5, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "alert")
        assert comp["message"] == "Watch out!"
        assert comp["level"] == "warning"
        assert comp["size"] == 0.5


class TestBigNumber:
    def test_returns_value(self, mock_preswald_service):
        from preswald.interfaces.components import big_number
        result = big_number(42, label="Score", component_id="test-id")
        assert result == "42"

    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import big_number
        big_number(42, label="Score", delta="+5", delta_color="green",
                   icon="star", description="Total", size=0.5, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "big_number")
        assert comp["value"] == 42
        assert comp["label"] == "Score"
        assert comp["delta"] == "+5"
        assert comp["delta_color"] == "green"
        assert comp["icon"] == "star"
        assert comp["description"] == "Total"


class TestButton:
    def test_returns_default_false(self, mock_preswald_service):
        from preswald.interfaces.components import button
        result = button("Click me", component_id="test-id")
        assert result is False

    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import button
        button("Click me", variant="primary", disabled=True, loading=True,
               size=0.5, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "button")
        assert comp["label"] == "Click me"
        assert comp["variant"] == "primary"
        assert comp["disabled"] is True
        assert comp["loading"] is True
        assert comp["onClick"] is True


class TestCheckbox:
    def test_returns_default(self, mock_preswald_service):
        from preswald.interfaces.components import checkbox
        result = checkbox("Accept", default=True, component_id="test-id")
        assert result is True

    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import checkbox
        checkbox("Accept", default=True, size=0.5, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "checkbox")
        assert comp["label"] == "Accept"
        assert comp["value"] is True


class TestGeneric:
    def test_fallback(self, mock_preswald_service):
        from preswald.interfaces.components import generic
        with patch("preswald.interfaces.render.registry.get_component_type_for_mimetype", return_value=None):
            result = generic("hello", mimetype="text/plain", component_id="test-id")
        assert result == "hello"

    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import generic
        with patch("preswald.interfaces.render.registry.get_component_type_for_mimetype", return_value=None):
            generic("hello", mimetype="text/plain", component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "generic")
        assert comp["mimetype"] == "text/plain"
        assert comp["value"] == "hello"


class TestImage:
    def test_returns_component(self, mock_preswald_service):
        from preswald.interfaces.components import image
        result = image("https://example.com/img.png", alt="Example", component_id="test-id")
        # image returns the component dict as its value
        assert isinstance(result, dict)

    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import image
        image("https://example.com/img.png", alt="Example", size=0.5, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "image")
        assert comp["src"] == "https://example.com/img.png"
        assert comp["alt"] == "Example"
        assert comp["size"] == 0.5


class TestJsonViewer:
    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import json_viewer
        json_viewer({"key": "value"}, title="Config", expanded=False,
                    size=0.5, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "json_viewer")
        assert comp["data"] == {"key": "value"}
        assert comp["title"] == "Config"
        assert comp["expanded"] is False

    def test_parses_json_string(self, mock_preswald_service):
        from preswald.interfaces.components import json_viewer
        json_viewer('{"a": 1}', component_id="test-id")
        comp = _get_component(mock_preswald_service)
        assert comp["data"] == {"a": 1}


class TestMatplotlib:
    def test_component_dict(self, mock_preswald_service):
        import matplotlib.pyplot as plt
        from preswald.interfaces.components import matplotlib as mpl_component
        fig, ax = plt.subplots()
        ax.plot([1, 2], [3, 4])
        mpl_component(fig=fig, label="my-plot", component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "matplotlib")
        assert comp["label"] == "my-plot"
        assert isinstance(comp["image"], str)
        assert len(comp["image"]) > 0  # base64 data
        plt.close(fig)


class TestPlotly:
    def test_component_dict(self, mock_preswald_service):
        import plotly.graph_objects as go
        from preswald.interfaces.components import plotly as plotly_component
        fig = go.Figure(data=go.Scatter(x=[1, 2], y=[3, 4]))
        plotly_component(fig, size=0.5, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "plot")  # plotly uses type "plot"
        assert "data" in comp
        assert isinstance(comp["data"]["data"], list)
        assert isinstance(comp["data"]["layout"], dict)
        assert comp["size"] == 0.5


class TestProgress:
    def test_returns_value(self, mock_preswald_service):
        from preswald.interfaces.components import progress
        result = progress("Loading", value=0.75, component_id="test-id")
        assert result == 0.75

    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import progress
        progress("Loading", value=0.75, size=0.5, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "progress")
        assert comp["label"] == "Loading"
        assert comp["value"] == 0.75


class TestSelectbox:
    def test_returns_default(self, mock_preswald_service):
        from preswald.interfaces.components import selectbox
        result = selectbox("Pick", options=["a", "b", "c"], default="b",
                           component_id="test-id")
        assert result == "b"

    def test_returns_first_option_when_no_default(self, mock_preswald_service):
        from preswald.interfaces.components import selectbox
        result = selectbox("Pick", options=["x", "y"], component_id="test-id")
        assert result == "x"

    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import selectbox
        selectbox("Pick", options=["a", "b"], default="a", size=0.5,
                  component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "selectbox")
        assert comp["label"] == "Pick"
        assert comp["options"] == ["a", "b"]
        assert comp["value"] == "a"


class TestSeparator:
    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import separator
        separator(component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "separator")


class TestSidebar:
    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import sidebar
        sidebar(defaultopen=True, logo="logo.png", name="MyApp",
                component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "sidebar")
        assert comp["defaultopen"] is True
        assert comp["branding"]["logo"] == "logo.png"
        assert comp["branding"]["name"] == "MyApp"


class TestSlider:
    def test_returns_default(self, mock_preswald_service):
        from preswald.interfaces.components import slider
        result = slider("Volume", min_val=0, max_val=100, step=5,
                        default=50, component_id="test-id")
        assert result == 50

    def test_returns_min_when_no_default(self, mock_preswald_service):
        from preswald.interfaces.components import slider
        result = slider("Volume", min_val=10, max_val=100,
                        component_id="test-id")
        assert result == 10

    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import slider
        slider("Volume", min_val=0, max_val=100, step=5, default=50,
               size=0.5, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "slider")
        assert comp["label"] == "Volume"
        assert comp["min"] == 0
        assert comp["max"] == 100
        assert comp["step"] == 5
        assert comp["value"] == 50


class TestSpinner:
    def test_returns_none(self, mock_preswald_service):
        from preswald.interfaces.components import spinner
        result = spinner(label="Please wait", component_id="test-id")
        assert result is None

    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import spinner
        spinner(label="Please wait", variant="card", show_label=False,
                size=0.5, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "spinner")
        assert comp["label"] == "Please wait"
        assert comp["variant"] == "card"
        assert comp["showLabel"] is False


class TestTable:
    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import table
        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})
        table(df, title="People", limit=1, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "table")
        assert comp["props"]["title"] == "People"
        assert len(comp["props"]["rowData"]) == 1  # limit=1
        assert len(comp["props"]["columnDefs"]) == 2

    def test_without_limit(self, mock_preswald_service):
        from preswald.interfaces.components import table
        df = pd.DataFrame({"x": [1, 2, 3]})
        table(df, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        assert len(comp["props"]["rowData"]) == 3


class TestText:
    def test_returns_value(self, mock_preswald_service):
        from preswald.interfaces.components import text
        result = text("# Hello", component_id="test-id")
        assert result == "# Hello"

    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import text
        text("# Hello", size=0.5, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "text")
        assert comp["markdown"] == "# Hello"
        assert comp["value"] == "# Hello"
        assert comp["size"] == 0.5


class TestTextInput:
    def test_returns_default(self, mock_preswald_service):
        from preswald.interfaces.components import text_input
        result = text_input("Name", default="Alice", component_id="test-id")
        assert result == "Alice"

    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import text_input
        text_input("Name", placeholder="Enter name", default="Alice",
                   size=0.5, component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "text_input")
        assert comp["label"] == "Name"
        assert comp["placeholder"] == "Enter name"
        assert comp["value"] == "Alice"
        assert comp["size"] == 0.5


class TestTopbar:
    def test_component_dict(self, mock_preswald_service):
        from preswald.interfaces.components import topbar
        topbar(component_id="test-id")
        comp = _get_component(mock_preswald_service)
        _assert_base(comp, "topbar")
