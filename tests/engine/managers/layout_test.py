from typing import Any

import pytest

from preswald.engine.managers.layout import LayoutManager
from preswald.interfaces.components import (
    TextComponent,
    ButtonComponent,
    SeparatorComponent,
    ValidationError,
)

@pytest.fixture
def layout_manager() -> LayoutManager:
    return LayoutManager()

def test_add_component_basic(layout_manager: LayoutManager) -> None:
    """Test adding a single component"""
    component = TextComponent(label="test", size=1.0, markdown="test")
    layout_manager.add_component(component)
    layout_manager.finish_current_row()
    
    assert len(layout_manager.rows) == 1
    assert len(layout_manager.rows[0]) == 1
    assert layout_manager.rows[0][0] == component

def test_add_multiple_components_same_row(layout_manager: LayoutManager) -> None:
    """Test adding multiple components that fit in one row"""
    component1 = TextComponent(label="test1", size=0.5, markdown="test1")
    component2 = TextComponent(label="test2", size=0.5, markdown="test2")
    
    layout_manager.add_component(component1)
    layout_manager.add_component(component2)
    layout_manager.finish_current_row()
    
    assert len(layout_manager.rows) == 1
    assert len(layout_manager.rows[0]) == 2
    assert layout_manager.rows[0][0] == component1
    assert layout_manager.rows[0][1] == component2

def test_add_components_multiple_rows(layout_manager: LayoutManager) -> None:
    """Test components split into multiple rows when they exceed size 1.0"""
    component1 = TextComponent(label="test1", size=0.6, markdown="test1")
    component2 = TextComponent(label="test2", size=0.6, markdown="test2")
    
    layout_manager.add_component(component1)
    layout_manager.add_component(component2)
    layout_manager.finish_current_row()
    
    assert len(layout_manager.rows) == 2
    assert len(layout_manager.rows[0]) == 1
    assert len(layout_manager.rows[1]) == 1
    assert layout_manager.rows[0][0] == component1
    assert layout_manager.rows[1][0] == component2

def test_separator_forces_new_row(layout_manager: LayoutManager) -> None:
    """Test that separator component forces a new row"""
    component1 = TextComponent(label="test1", size=0.5, markdown="test1")
    separator = SeparatorComponent(label="sep", size=1.0)
    component2 = TextComponent(label="test2", size=0.5, markdown="test2")
    
    layout_manager.add_component(component1)
    layout_manager.add_component(separator)
    layout_manager.add_component(component2)
    layout_manager.finish_current_row()
    
    assert len(layout_manager.rows) == 3
    assert len(layout_manager.rows[0]) == 1
    assert len(layout_manager.rows[1]) == 0  # Separator creates empty row
    assert len(layout_manager.rows[2]) == 1

def test_flex_calculation(layout_manager: LayoutManager) -> None:
    """Test flex values are calculated correctly"""
    component1 = TextComponent(label="test1", size=0.3, markdown="test1")
    component2 = TextComponent(label="test2", size=0.7, markdown="test2")
    
    layout_manager.add_component(component1)
    layout_manager.add_component(component2)
    layout_manager.finish_current_row()
    
    layout_dict = layout_manager.get_layout()
    assert len(layout_dict) == 1
    assert len(layout_dict[0]) == 2
    
    assert layout_dict[0][0]["flex"] == 0.3
    assert layout_dict[0][1]["flex"] == 0.7

def test_clear_layout(layout_manager: LayoutManager) -> None:
    """Test clearing the layout"""
    component = TextComponent(label="test", size=1.0, markdown="test")
    layout_manager.add_component(component)
    layout_manager.finish_current_row()
    
    assert len(layout_manager.rows) == 1
    
    layout_manager.clear_layout()
    assert len(layout_manager.rows) == 0
    assert len(layout_manager.current_row) == 0
    assert layout_manager.current_row_size == 0.0
    assert len(layout_manager.seen_ids) == 0

def test_component_id_tracking(layout_manager: LayoutManager) -> None:
    """Test that component IDs are tracked correctly"""
    component1 = TextComponent(label="test1", size=0.5, markdown="test1")
    component2 = TextComponent(label="test2", size=0.5, markdown="test2")
    
    layout_manager.add_component(component1)
    layout_manager.add_component(component2)
    
    assert component1.id in layout_manager.seen_ids
    assert component2.id in layout_manager.seen_ids

def test_get_layout_conversion(layout_manager: LayoutManager) -> None:
    """Test that get_layout returns correct dictionary format"""
    component = ButtonComponent(label="test", size=1.0)
    layout_manager.add_component(component)
    layout_manager.finish_current_row()
    
    layout = layout_manager.get_layout()
    assert len(layout) == 1
    assert len(layout[0]) == 1
    
    component_dict = layout[0][0]
    assert component_dict["type"] == "button"
    assert component_dict["label"] == "test"
    assert component_dict["size"] == 1.0
    assert component_dict["id"] == component.id
    assert "flex" in component_dict 
