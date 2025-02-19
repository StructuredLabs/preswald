from typing import Any

from preswald.interfaces.components import BaseComponent

class LayoutManager:
    """Manages the layout of components in rows based on their sizes"""

    def __init__(self) -> None:
        self.rows: list[list[BaseComponent]] = []
        self.current_row: list[BaseComponent] = []
        self.current_row_size = 0.0
        self.seen_ids: set[str] = set()

    def add_component(self, component: BaseComponent) -> None:
        """Add a component to the layout"""
        # Handle separator component type which forces a new row
        if component.type == "separator":
            self.finish_current_row()
            return

        # If component size is greater than remaining space, start new row
        if self.current_row_size + component.size > 1.0:
            self.finish_current_row()

        # Add component to current row
        self.current_row.append(component)
        self.current_row_size += component.size

        # If row is exactly full, finish it
        if self.current_row_size >= 1.0:
            self.finish_current_row()

        self.seen_ids.add(component.id)

    def finish_current_row(self) -> None:
        """Complete current row and start a new one"""
        if self.current_row:
            # Calculate flex values for the row
            total_size = sum(c.size for c in self.current_row)
            for component in self.current_row:
                component.set_flex_from_total(total_size)

            self.rows.append(self.current_row)
            self.current_row = []
            self.current_row_size = 0.0

    def get_layout(self) -> list[list[dict[str, Any]]]:
        """Get the final layout with all components organized in rows"""
        self.finish_current_row()  # Ensure any remaining components are added
        return [[c.to_dict() for c in row] for row in self.rows]

    def clear_layout(self) -> None:
        """Clear the layout"""
        self.rows.clear()
        self.current_row.clear()
        self.current_row_size = 0.0
        self.seen_ids = set()
