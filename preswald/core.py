from markdown import markdown
import pandas as pd
from sqlalchemy import create_engine
from preswald.state import StateManager
from functools import wraps
from typing import Dict, Any, Optional, Callable
import json
import logging
import uuid
import threading
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global store for connections and rendered components
connections = {}
_rendered_html = []
_component_states: Dict[str, Any] = {}
_component_callbacks: Dict[str, List[Callable]] = {}
_state_lock = threading.Lock()

# Create a global state manager
state_manager = StateManager()

def register_component_callback(component_id: str, callback: Callable):
    """Register a callback for component state changes"""
    with _state_lock:
        if component_id not in _component_callbacks:
            _component_callbacks[component_id] = []
        _component_callbacks[component_id].append(callback)
        logger.debug(f"[STATE] Registered callback for component {component_id}")
        logger.debug(f"  - Total callbacks: {len(_component_callbacks[component_id])}")

def update_component_state(component_id: str, value: Any):
    """Update the state of a component and trigger callbacks"""
    with _state_lock:
        logger.debug(f"[STATE] Updating state for component {component_id}: {value}")
        old_value = _component_states.get(component_id)
        _component_states[component_id] = value
        
        # Log state change
        logger.debug(f"[STATE] State changed for {component_id}:")
        logger.debug(f"  - Old value: {old_value}")
        logger.debug(f"  - New value: {value}")
        
        # Trigger callbacks if any
        if component_id in _component_callbacks:
            logger.debug(f"[STATE] Triggering {len(_component_callbacks[component_id])} callbacks for {component_id}")
            for callback in _component_callbacks[component_id]:
                try:
                    callback(value)
                    logger.debug(f"[STATE] Successfully executed callback for {component_id}")
                except Exception as e:
                    logger.error(f"[STATE] Error in callback for component {component_id}: {e}")

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

def clear_component_states():
    """Clear all component states"""
    with _state_lock:
        logger.debug("[STATE] Clearing all component states")
        _component_states.clear()
        _component_callbacks.clear()

def track(func):
    """Decorator to track function calls and their dependencies"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Register this function call
        node_id = state_manager.track_function_call(func, args, kwargs)

        # Get or compute the result
        return state_manager.get_or_compute(node_id)

    return wrapper

def connect(source, name=None):
    """
    Connect to a data source such as a CSV, JSON, or database.

    Args:
        source (str): Path to a file or database connection string.
        name (str, optional): A unique name for the connection.
    """
    if name is None:
        name = f"connection_{len(connections) + 1}"

    try:
        if source.endswith(".csv"):
            # Get script directory and make path relative to it
            import os
            from preswald.server import SCRIPT_PATH
            script_dir = os.path.dirname(SCRIPT_PATH)
            # Make source path absolute if it's relative
            if not os.path.isabs(source):
                csv_path = os.path.join(script_dir, source)
            else:
                csv_path = source
            connections[name] = pd.read_csv(csv_path)
        elif source.endswith(".json"):
            connections[name] = pd.read_json(source)
        elif source.endswith(".parquet"):
            connections[name] = pd.read_parquet(source)
        elif any(source.startswith(prefix) for prefix in ["postgresql://", "postgres://", "mysql://"]):
            engine = create_engine(source)
            connections[name] = engine
        else:
            raise ValueError(f"Unsupported data source format: {source}")
    except Exception as e:
        raise RuntimeError(f"Failed to connect to source '{source}': {e}")

    return name


def get_connection(name):
    """
    Retrieve a connection by name.

    Args:
        name (str): The name of the connection.
    """
    if name not in connections:
        raise ValueError(f"No connection found with name '{name}'")
    return connections[name]


def view(connection_name, limit=50):
    """
    Render a data preview table based on the connection.

    Args:
        connection_name (str): Name of the connection to display.
        limit (int): Maximum number of rows to display.
    """
    connection = get_connection(connection_name)
    if isinstance(connection, pd.DataFrame):
        html_table = connection.head(limit).to_html(
            index=False, classes="table table-striped"
        )
        _rendered_html.append(html_table)
    else:
        raise TypeError(f"Connection '{connection_name}' is not a valid DataFrame")


def get_rendered_html():
    """
    Retrieve all rendered components as a single HTML string.
    """
    global _rendered_html
    html_output = "".join(_rendered_html)
    _rendered_html.clear()
    return html_output


def execute_query(connection_name, query):
    """
    Execute a SQL query on a database connection.

    Args:
        connection_name (str): Name of the database connection.
        query (str): The SQL query to execute.
    """
    connection = get_connection(connection_name)

    if not isinstance(connection, create_engine().__class__):
        raise TypeError(f"Connection '{connection_name}' is not a database connection")

    with connection.connect() as conn:
        result = pd.read_sql(query, conn)
        return result

def get_rendered_components():
    """Get all rendered components as JSON"""
    logger.debug(f"Getting rendered components, count: {len(_rendered_html)}")
    components = []
    
    # Create a set to track unique component IDs
    seen_ids = set()
    
    for item in _rendered_html:
        try:
            if isinstance(item, dict):
                # Ensure component has current state
                if 'id' in item:
                    component_id = item['id']
                    if component_id not in seen_ids:
                        # Update component with current state
                        if 'value' in item:
                            current_state = get_component_state(component_id, item['value'])
                            item['value'] = current_state
                        components.append(item)
                        seen_ids.add(component_id)
                        logger.debug(f"Added component with state: {item}")
            else:
                # Convert HTML string to component data
                component = {
                    "type": "html",
                    "content": str(item)
                }
                components.append(component)
                logger.debug(f"Converted HTML to component: {component}")
        except Exception as e:
            logger.error(f"Error processing component: {e}", exc_info=True)
    
    # Clear the rendered_html list after processing
    _rendered_html.clear()
    
    logger.info(f"Returning {len(components)} unique components")
    return components
