import pandas as pd
import pytest

from preswald.engine.runner import validate_dataframe_operation


def test_validate_dataframe_operation_valid():
    """Test validation with valid DataFrame and column."""
    df = pd.DataFrame({"Humidity": [0.5, 0.6, 0.7], "Temperature": [20, 25, 30]})
    validate_dataframe_operation(df, "Humidity", "filtering")


def test_validate_dataframe_operation_invalid_column():
    """Test validation with invalid column name."""
    df = pd.DataFrame({"Humidity": [0.5, 0.6, 0.7], "Temperature": [20, 25, 30]})
    with pytest.raises(
        ValueError, match="Column 'value' not found in DataFrame for filtering"
    ):
        validate_dataframe_operation(df, "value", "filtering")


def test_validate_dataframe_operation_invalid_type():
    """Test validation with invalid DataFrame type."""
    with pytest.raises(ValueError, match="Expected DataFrame, got str"):
        validate_dataframe_operation("not a dataframe", "value", "filtering")


def test_validate_dataframe_operation_empty_dataframe():
    """Test validation with empty DataFrame."""
    df = pd.DataFrame()
    with pytest.raises(
        ValueError, match="Column 'value' not found in DataFrame for filtering"
    ):
        validate_dataframe_operation(df, "value", "filtering")
