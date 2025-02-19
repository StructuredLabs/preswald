from typing import Any

import pytest
import pandas as pd

from preswald.interfaces.components import (
    CheckboxComponent,
    SliderComponent,
    TableComponent,
    TextComponent,
)
from preswald.errors import ValidationError

@pytest.fixture
def mock_service(mocker: Any) -> Any:
    service = mocker.patch('preswald.engine.service.PreswaldService')
    service.get_instance.return_value.get_component_state.return_value = None
    return service

def test_component_size_validation() -> None:
    """Test that component size must be between 0 and 1"""
    with pytest.raises(ValidationError) as error:
        TextComponent(label="header", size=1.5, markdown="test")
    assert str(error.value) == "text component 'header' has invalid size 1.5. Size must be between 0 and 1"

    with pytest.raises(ValidationError) as error:
        TextComponent(label="footer", size=0, markdown="test")
    assert str(error.value) == "text component 'footer' has invalid size 0. Size must be between 0 and 1"

    with pytest.raises(ValidationError) as error:
        TextComponent(label="sidebar", size=-0.5, markdown="test")
    assert str(error.value) == "text component 'sidebar' has invalid size -0.5. Size must be between 0 and 1"

    # Valid sizes should work
    TextComponent(label="test", size=0.5, markdown="test")
    TextComponent(label="test", size=1.0, markdown="test")
    TextComponent(label="test", size=0.1, markdown="test") 

@pytest.mark.parametrize("service_value, default, expected", [
    (None, False, False),  # No value from service, use default False
    (None, True, True),    # No value from service, use default True
    (True, False, True),   # Service returns True, ignore default False
    (False, True, False),  # Service returns False, ignore default True
])
def test_checkbox_component(
    mock_service: Any,
    service_value: bool | None,
    default: bool,
    expected: bool
) -> None:
    mock_service.get_instance.return_value.get_component_state.return_value = service_value
    checkbox = CheckboxComponent(label="test", size=1.0, default=default)
    assert checkbox.id.startswith("checkbox-")
    assert checkbox.value == expected
    assert checkbox.default == default

def test_slider_component_fails_validation() -> None:
    """Fail if min is greater than max"""
    with pytest.raises(ValidationError) as error:
        SliderComponent(
            label="temperature",
            size=1.0,
            min=10,
            max=0,
            step=1,
        )
    assert str(error.value) == "slider component 'temperature' has invalid range: min value (10) must be less than max value (0)"

def test_slider_component_with_invalid_step() -> None:
    """Fail if step is less than or equal to 0"""
    with pytest.raises(ValidationError) as error:
        SliderComponent(
            label="volume",
            size=1.0,
            min=0,
            max=10,
            step=0,
        )
    assert str(error.value) == "slider component 'volume' has invalid step: value (0) must be greater than 0"

@pytest.mark.parametrize("service_value, default, expected", [
    (None, 0, 0),  # No value from service, use default 0
    (None, 5, 5),    # No value from service, use default 5
    (10, 0, 10),   # Service returns 10, ignore default 0
    (5, 10, 5),  # Service returns 5, ignore default 10
])
def test_slider_component(mock_service, service_value, default, expected):
    # Configure mock service to return specific value
    mock_service.get_instance.return_value.get_component_state.return_value = service_value

    slider = SliderComponent(
        label="test",
        min=0,
        max=10,
        step=1,
        default=default,
    )

    assert slider.id.startswith("slider-")
    assert slider.value == expected
    assert slider.default == default
    assert slider.min == 0
    assert slider.max == 10

def test_table_component_with_dataframe() -> None:
    df = pd.DataFrame({
        "a": [1, 2, 3],
        "b": ["x", "y", "z"]
    })
    table = TableComponent(label="test", size=1.0, raw_data=df)
    assert len(table.data) == 3
    assert table.data[0] == {"a": 1, "b": "x"}

def test_table_component_with_dict_list() -> None:
    data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
    table = TableComponent(label="test", size=1.0, raw_data=data)
    assert len(table.data) == 2
    assert table.data[0] == {"name": "John", "age": 30}

def test_table_component_with_primitive_list() -> None:
    data = ["a", "b", "c"]
    table = TableComponent(label="test", size=1.0, raw_data=data)
    assert len(table.data) == 3
    assert table.data[0] == {"value": "a"}

def test_table_component_with_single_object():
    data = {"total": 100}
    table = TableComponent(label="test", raw_data=data)
    assert len(table.data) == 1
    assert table.data[0] == {"total": 100}