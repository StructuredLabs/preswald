import pytest
from preswald.interfaces.components import button, slider, checkbox, text_input, selectbox, progress


def test_button():
    result = button("Click Me")
    assert "Click Me" in result
    assert "button" in result


def test_slider():
    result = slider("Adjust Value", min_val=0, max_val=100, step=5, default=50)
    assert "range" in result
    assert 'min="0"' in result
    assert 'max="100"' in result
    assert 'step="5"' in result
    assert 'value="50"' in result


def test_checkbox():
    result = checkbox("Accept Terms", default=True)
    assert "checkbox" in result
    assert "Accept Terms" in result
    assert "checked" in result


def test_text_input():
    result = text_input("Name", placeholder="Enter your name")
    assert "Name" in result
    assert 'placeholder="Enter your name"' in result


def test_selectbox():
    options = ["Apple", "Banana", "Cherry"]
    result = selectbox("Choose Fruit", options, default="Banana")
    assert "Choose Fruit" in result
    assert "Banana" in result
    assert "Apple" in result
    assert "Cherry" in result


def test_progress():
    result = progress("Upload Progress", value=70)
    assert "progress" in result
    assert 'value="70"' in result
