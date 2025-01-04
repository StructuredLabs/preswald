from markdown import markdown
import pandas as pd
from sqlalchemy import create_engine
from typing import Dict, Any, Optional, Callable
import json
import logging
import uuid
import threading
from typing import Dict, List
import asyncio
import numpy as np

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global store for connections and rendered components
connections = {}
_rendered_html = []
_component_states: Dict[str, Any] = {}
_component_callbacks: Dict[str, List[Callable]] = {}
_state_lock = threading.Lock()


def register_component_callback(component_id: str, callback: Callable):
    """Register a callback for component state changes"""
    with _state_lock:
        if component_id not in _component_callbacks:
            _component_callbacks[component_id] = []
        _component_callbacks[component_id].append(callback)
        logger.debug(f"[STATE] Registered callback for component {component_id}")
        logger.debug(f"  - Total callbacks: {len(_component_callbacks[component_id])}")

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
        if obj.dtype.kind in ['f', 'c']:  # Float or complex
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
            
            # Trigger callbacks if any
            if component_id in _component_callbacks:
                logger.debug(f"[STATE] Triggering {len(_component_callbacks[component_id])} callbacks for {component_id}")
                for callback in _component_callbacks[component_id]:
                    try:
                        callback(cleaned_value)
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
        logger.debug("[STATE] Clearing component callbacks")
        _component_callbacks.clear()
        # Do not clear _component_states as we want to preserve values between reruns

async def broadcast_connections():
    """Broadcast current connections to all clients"""
    try:
        connection_list = []
        for name, conn in connections.items():
            conn_type = type(conn).__name__
            conn_info = {
                "name": name,
                "type": conn_type,
                "details": str(conn)[:100] + "..." if len(str(conn)) > 100 else str(conn)
            }
            connection_list.append(conn_info)
        
        # Import here to avoid circular imports
        from preswald.server import broadcast_message
        await broadcast_message({
            "type": "connections_update",
            "connections": connection_list
        })
    except Exception as e:
        logger.error(f"Error broadcasting connections: {e}")

def connect(source, name=None):
    """
    Connect to a data source such as a CSV, JSON, or database.
    If source is a connection name from config.toml, it will use that configuration.
    Otherwise, it will treat source as a direct file path or connection string.

    Args:
        source (str): Either a connection name from config.toml or a direct path/connection string
        name (str, optional): A unique name for the connection
    """
    if name is None:
        name = f"connection_{len(connections) + 1}"

    # Check if connection with this name already exists
    if name in connections:
        logger.info(f"[CONNECT] Connection '{name}' already exists, reusing existing connection")
        return name

    try:
        # First try to load from config if it's a connection name
        try:
            from preswald.data import load_connection_config
            from preswald.server import SCRIPT_PATH
            import os
            
            if SCRIPT_PATH:
                config_dir = os.path.dirname(SCRIPT_PATH)
                config_path = os.path.join(config_dir, "config.toml")
                secrets_path = os.path.join(config_dir, "secrets.toml")
                
                if os.path.exists(config_path):
                    config = load_connection_config(config_path, secrets_path)
                    if source in config:
                        # Use the named connection from config
                        conn_config = config[source]
                        if conn_config.get('type') == 'postgres':
                            user = conn_config.get('user', 'postgres')
                            password = conn_config.get('password', '')
                            host = conn_config.get('host', 'localhost')
                            port = conn_config.get('port', 5432)
                            dbname = conn_config.get('dbname', 'postgres')
                            source = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
                        elif conn_config.get('type') == 'mysql':
                            user = conn_config.get('user', 'root')
                            password = conn_config.get('password', '')
                            host = conn_config.get('host', 'localhost')
                            port = conn_config.get('port', 3306)
                            dbname = conn_config.get('dbname', '')
                            source = f"mysql://{user}:{password}@{host}:{port}/{dbname}"
                        elif conn_config.get('type') in ['csv', 'json', 'parquet']:
                            source = conn_config.get('path')
                        else:
                            raise ValueError(f"Unsupported connection type: {conn_config.get('type')}")
        except Exception as e:
            # If loading from config fails, continue with direct source
            logger.warning(f"[CONNECT] Failed to load from config: {e}")
            pass

        # Process the source as a direct path/connection string
        if source.endswith(".csv"):
            # Get script directory and make path relative to it
            import os
            from preswald.server import SCRIPT_PATH
            import requests
            
            # Check if source is a URL
            if source.startswith(("http://", "https://")):
                response = requests.get(source)
                response.raise_for_status()  # Raise error for bad status codes
                # Create a StringIO object from the response content
                from io import StringIO
                csv_data = StringIO(response.text)
                connections[name] = pd.read_csv(csv_data)
            else:
                # Handle local file path
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

        # Broadcast connection updates
        asyncio.create_task(broadcast_connections())
        logger.info(f"[CONNECT] Successfully created connection '{name}' to {source}")
    except Exception as e:
        # Clean up if connection failed
        if name in connections:
            del connections[name]
        raise RuntimeError(f"Failed to connect to source '{source}': {e}")

    return name

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
        if hasattr(connection, 'dispose'):
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

def clear_rendered_components():
    """Clear all rendered components"""
    global _rendered_html
    logger.debug("[CORE] Clearing all rendered components")
    _rendered_html.clear()

def convert_to_serializable(obj):
    """Convert numpy arrays and other non-serializable objects to Python native types."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.int8, np.int16, np.int32, np.int64, np.integer)):
        return int(obj)
    elif isinstance(obj, (np.float16, np.float32, np.float64, np.floating)):
        if np.isnan(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, np.generic):
        if hasattr(obj, 'item'):
            val = obj.item()
            if isinstance(val, float) and np.isnan(val):
                return None
            return val
        return None
    return obj

def get_rendered_components():
    """Get all rendered components as JSON"""
    logger.debug(f"[CORE] Getting rendered components, count: {len(_rendered_html)}")
    components = []
    
    # Create a set to track unique component IDs
    seen_ids = set()
    
    for item in _rendered_html:
        try:
            if isinstance(item, dict):
                # Clean any NaN values in the component
                cleaned_item = _clean_nan_values(item)
                
                # Ensure component has current state
                if 'id' in cleaned_item:
                    component_id = cleaned_item['id']
                    if component_id not in seen_ids:
                        # Update component with current state if it exists
                        if 'value' in cleaned_item:
                            current_state = get_component_state(component_id)
                            if current_state is not None:
                                cleaned_item['value'] = _clean_nan_values(current_state)
                                logger.debug(f"[CORE] Updated component {component_id} with state: {current_state}")
                        components.append(cleaned_item)
                        seen_ids.add(component_id)
                        logger.debug(f"[CORE] Added component with state: {cleaned_item}")
                else:
                    # Components without IDs are added as-is
                    components.append(cleaned_item)
                    logger.debug(f"[CORE] Added component without ID: {cleaned_item}")
            else:
                # Convert HTML string to component data
                component = {
                    "type": "html",
                    "content": str(item)
                }
                components.append(component)
                logger.debug(f"[CORE] Added HTML component: {component}")
        except Exception as e:
            logger.error(f"[CORE] Error processing component: {e}", exc_info=True)
            continue
    
    return components
