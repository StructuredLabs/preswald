class LayoutManager:
    """Manages the layout of components in rows based on their sizes"""

    def __init__(self):
        self.rows = []
        self.current_row = []
        self.current_row_size = 0.0
        self.seen_ids = set()

    def add_component(self, component):
        """Add a component to the layout"""
        size = float(component.get("size", 1.0))

        if "id" in component:
            self.seen_ids.add(component["id"])

        # Handle separator component type which forces a new row
        if component.get("type") == "separator":
            self.finish_current_row()
            # Add separator in its own row
            self.rows.append([component])
            return

        # If component size is greater than remaining space, start new row
        if self.current_row_size + size > 1.0:
            self.finish_current_row()

        # Add component to current row
        self.current_row.append(component)
        self.current_row_size += size

        # If row is exactly full, finish it
        if self.current_row_size >= 1.0:
            self.finish_current_row()

    def finish_current_row(self):
        """Complete current row and start a new one"""
        if self.current_row:
            # Calculate flex values for the row
            total_size = sum(float(c.get("size", 1.0)) for c in self.current_row)
            for component in self.current_row:
                component_size = float(component.get("size", 1.0))
                component["flex"] = component_size / total_size

            self.rows.append(self.current_row)
            self.current_row = []
            self.current_row_size = 0.0

    def get_layout(self):
        """Get the final layout with all components organized in rows"""
        self.finish_current_row()  # Ensure any remaining components are added
        return self.rows

    def clear_layout(self):
        """Clear the layout"""
        self.rows.clear()
        self.current_row.clear()
        self.current_row_size = 0.0
        self.seen_ids = set()
