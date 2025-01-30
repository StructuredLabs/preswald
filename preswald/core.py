# TODO(jayanth): marked for deletion

from typing import Dict, Any, Callable, List
import logging
import threading
import asyncio
import time

# Configure logging
logger = logging.getLogger(__name__)

# Global store for connections and rendered components
connections = {}
_rendered_html = []
_component_states: Dict[str, Any] = {}
_state_lock = threading.Lock()


def get_script_path():
    """Get the script path from the server module, avoiding circular imports."""
    from preswald.server import SCRIPT_PATH

    return SCRIPT_PATH


def _clean_nan_values(obj):
    """Clean NaN values from an object recursively."""
    import numpy as np

    if isinstance(obj, (float, np.floating)):
        return None if np.isnan(obj) else float(obj)
    elif isinstance(obj, (list, tuple)):
        return [_clean_nan_values(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: _clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, np.ndarray):
        if obj.dtype.kind in ["f", "c"]:  # Float or complex
            obj = np.where(np.isnan(obj), None, obj)
        return obj.tolist()
    return obj


def update_component_state(component_id: str, value: Any):
    """Update the state of a component and trigger callbacks"""
    with _state_lock:
        logger.debug(f"[STATE] Updating state for component {component_id}: {value}")
        old_value = _component_states.get(component_id)

        # Clean NaN values before comparison and storage
        cleaned_value = _clean_nan_values(value)
        cleaned_old_value = _clean_nan_values(old_value)

        if cleaned_old_value != cleaned_value:  # Only update if value has changed
            _component_states[component_id] = cleaned_value

            # Log state change
            logger.debug(f"[STATE] State changed for {component_id}:")
            logger.debug(f"  - Old value: {cleaned_old_value}")
            logger.debug(f"  - New value: {cleaned_value}")


def get_component_state(component_id: str, default: Any = None) -> Any:
    """Get the current state of a component"""
    with _state_lock:
        value = _component_states.get(component_id, default)
        logger.debug(f"[STATE] Getting state for {component_id}: {value}")
        return value


def get_all_component_states() -> Dict[str, Any]:
    """Get all component states"""
    with _state_lock:
        states = dict(_component_states)
        logger.debug(f"[STATE] Getting all states: {states}")
        return states


async def broadcast_connections():
    """Broadcast current connections to all clients"""
    try:
        connection_list = []
        for name, conn in connections.items():
            conn_type = type(conn).__name__
            conn_info = {
                "name": name,
                "type": conn_type,
                "details": (
                    str(conn)[:100] + "..." if len(str(conn)) > 100 else str(conn)
                ),
            }
            connection_list.append(conn_info)

        # Import here to avoid circular imports
        from preswald.server import broadcast_message

        await broadcast_message(
            {"type": "connections_update", "connections": connection_list}
        )
    except Exception as e:
        logger.error(f"Error broadcasting connections: {e}")


def disconnect(name: str):
    """
    Disconnect and clean up a connection.

    Args:
        name (str): The name of the connection to disconnect.
    """
    if name not in connections:
        logger.warning(f"[DISCONNECT] No connection found with name '{name}'")
        return

    try:
        connection = connections[name]
        # Close database connections
        if hasattr(connection, "dispose"):
            connection.dispose()

        # Remove from connections dict
        del connections[name]
        logger.info(f"[DISCONNECT] Successfully disconnected '{name}'")

        # Broadcast updated connections list
        asyncio.create_task(broadcast_connections())
    except Exception as e:
        logger.error(f"[DISCONNECT] Error disconnecting '{name}': {e}")
        raise


def get_connection(name):
    """
    Retrieve a connection by name.

    Args:
        name (str): The name of the connection.
    """
    if name not in connections:
        raise ValueError(f"No connection found with name '{name}'")
    return connections[name]


def clear_rendered_components():
    """Clear all rendered components"""
    global _rendered_html
    logger.debug("[CORE] Clearing all rendered components")
    _rendered_html.clear()


class LayoutManager:
    """Manages the layout of components in rows based on their sizes"""

    def __init__(self):
        self.rows = []
        self.current_row = []
        self.current_row_size = 0.0

    def add_component(self, component):
        """Add a component to the layout"""
        size = float(component.get("size", 1.0))

        # Handle separator component type which forces a new row
        if component.get("type") == "separator":
            self.finish_current_row()
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


def get_rendered_components():
    """Get all rendered components as JSON, organized into rows"""
    start_time = time.time()
    logger.debug(f"[RENDER] Getting rendered components, count: {len(_rendered_html)}")

    # Create layout manager
    layout_manager = LayoutManager()
    seen_ids = set()

    # Process components
    for item in _rendered_html:
        try:
            if isinstance(item, dict):
                # Clean any NaN values in the component
                clean_start = time.time()
                cleaned_item = _clean_nan_values(item)
                logger.debug(
                    f"[RENDER] NaN cleanup took {time.time() - clean_start:.3f}s"
                )

                # Ensure component has current state
                if "id" in cleaned_item:
                    component_id = cleaned_item["id"]
                    if component_id not in seen_ids:
                        # Update component with current state if it exists
                        if "value" in cleaned_item:
                            current_state = get_component_state(component_id)
                            if current_state is not None:
                                cleaned_item["value"] = _clean_nan_values(current_state)
                                logger.debug(
                                    f"[RENDER] Updated component {component_id} with state: {current_state}"
                                )
                        layout_manager.add_component(cleaned_item)
                        seen_ids.add(component_id)
                        logger.debug(
                            f"[RENDER] Added component with state: {cleaned_item}"
                        )
                else:
                    # Components without IDs are added as-is
                    layout_manager.add_component(cleaned_item)
                    logger.debug(f"[RENDER] Added component without ID: {cleaned_item}")
            else:
                # Convert HTML string to component data
                component = {
                    "type": "html",
                    "content": str(item),
                    "size": 1.0,  # HTML components take full width
                }
                layout_manager.add_component(component)
                logger.debug(f"[RENDER] Added HTML component: {component}")
        except Exception as e:
            logger.error(f"[RENDER] Error processing component: {e}", exc_info=True)
            continue

    # Get final layout
    rows = layout_manager.get_layout()
    logger.debug(f"[RENDER] Total rendering took {time.time() - start_time:.3f}s")
    return {"rows": rows}
