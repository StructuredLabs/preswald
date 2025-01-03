import uuid
from preswald.core import _rendered_html, get_component_state
import logging
import numpy as np
import json
import pandas as pd
import hashlib

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_id(prefix="component"):
    """Generate a unique ID for a component."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def checkbox(label, default=False):
    """Create a checkbox component with consistent ID based on label."""
    # Create a consistent ID based on the label
    component_id = f"checkbox-{hashlib.md5(label.encode()).hexdigest()[:8]}"
    
    # Get current state or use default
    current_value = get_component_state(component_id)
    if current_value is None:
        current_value = default
    
    logger.debug(f"Creating checkbox component with id {component_id}, label: {label}")
    component = {
        "type": "checkbox",
        "id": component_id,
        "label": label,
        "value": current_value
    }
    logger.debug(f"Created component: {component}")
    _rendered_html.append(component)
    return component

def slider(label: str, min_val: float = 0.0, max_val: float = 100.0, step: float = 1.0, default: float = None) -> dict:
    """Create a slider component with consistent ID based on label"""
    # Create a consistent ID based on the label
    component_id = f"slider-{hashlib.md5(label.encode()).hexdigest()[:8]}"
    
    # Get current state or use default
    current_value = get_component_state(component_id)
    if current_value is None:
        current_value = default if default is not None else min_val
    
    component = {
        "type": "slider",
        "id": component_id,
        "label": label,
        "min": min_val,
        "max": max_val,
        "step": step,
        "value": current_value
    }
    
    logger.debug(f"Creating slider component with id {component_id}, label: {label}")
    logger.debug(f"Current value from state: {current_value}")
    
    _rendered_html.append(component)
    
    return component

def button(label):
    """Create a button component."""
    id = generate_id("button")
    logger.debug(f"Creating button component with id {id}, label: {label}")
    component = {
        "type": "button",
        "id": id,
        "label": label
    }
    logger.debug(f"Created component: {component}")
    _rendered_html.append(component)
    return component

def selectbox(label, options, default=None):
    """Create a select component with consistent ID based on label."""
    # Create a consistent ID based on the label
    component_id = f"selectbox-{hashlib.md5(label.encode()).hexdigest()[:8]}"
    
    # Get current state or use default
    current_value = get_component_state(component_id)
    if current_value is None:
        current_value = default if default is not None else (options[0] if options else None)
    
    logger.debug(f"Creating selectbox component with id {component_id}, label: {label}")
    component = {
        "type": "selectbox",
        "id": component_id,
        "label": label,
        "options": options,
        "value": current_value
    }
    logger.debug(f"Created component: {component}")
    _rendered_html.append(component)
    return component

def text_input(label, placeholder=""):
    """Create a text input component with consistent ID based on label."""
    # Create a consistent ID based on the label
    component_id = f"text_input-{hashlib.md5(label.encode()).hexdigest()[:8]}"
    
    # Get current state or use default
    current_value = get_component_state(component_id)
    if current_value is None:
        current_value = ""
    
    logger.debug(f"Creating text input component with id {component_id}, label: {label}")
    component = {
        "type": "text_input",
        "id": component_id,
        "label": label,
        "placeholder": placeholder,
        "value": current_value
    }
    logger.debug(f"Created component: {component}")
    _rendered_html.append(component)
    return component

def progress(label, value=0):
    """Create a progress component."""
    id = generate_id("progress")
    logger.debug(f"Creating progress component with id {id}, label: {label}")
    component = {
        "type": "progress",
        "id": id,
        "label": label,
        "value": value
    }
    logger.debug(f"Created component: {component}")
    _rendered_html.append(component)
    return component

def spinner(label):
    """Create a spinner component."""
    id = generate_id("spinner")
    logger.debug(f"Creating spinner component with id {id}, label: {label}")
    component = {
        "type": "spinner",
        "id": id,
        "label": label
    }
    logger.debug(f"Created component: {component}")
    _rendered_html.append(component)
    return component

def alert(message, level="info"):
    """Create an alert component."""
    id = generate_id("alert")
    logger.debug(f"Creating alert component with id {id}, message: {message}")
    component = {
        "type": "alert",
        "id": id,
        "message": message,
        "level": level
    }
    logger.debug(f"Created component: {component}")
    _rendered_html.append(component)
    return component

def image(src, alt="Image"):
    """Create an image component."""
    id = generate_id("image")
    logger.debug(f"Creating image component with id {id}, src: {src}")
    component = {
        "type": "image",
        "id": id,
        "src": src,
        "alt": alt
    }
    logger.debug(f"Created component: {component}")
    _rendered_html.append(component)
    return component

def text(markdown_str):
    """Create a text/markdown component."""
    id = generate_id("text")
    logger.debug(f"Creating text component with id {id}")
    component = {
        "type": "text",
        "id": id,
        "markdown": markdown_str,
        "value": markdown_str
    }
    logger.debug(f"Created component: {component}")
    _rendered_html.append(component)
    return component

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
        if np.isnan(obj):
            return None
        return obj.item()
    return obj

def plotly(fig):
    """
    Render a Plotly figure.

    Args:
        fig: A Plotly figure object.
    """
    try:
        id = generate_id("plot")
        logger.debug(f"Creating plot component with id {id}")
        
        # Convert the figure to JSON-serializable format
        fig_dict = fig.to_dict()
        
        # Clean up any NaN values in the data
        for trace in fig_dict.get('data', []):
            if isinstance(trace.get('marker'), dict):
                marker = trace['marker']
                if 'sizeref' in marker and (isinstance(marker['sizeref'], float) and np.isnan(marker['sizeref'])):
                    marker['sizeref'] = None
            
            # Clean up other potential NaN values
            for key, value in trace.items():
                if isinstance(value, (list, np.ndarray)):
                    trace[key] = [None if isinstance(x, (float, np.floating)) and np.isnan(x) else x for x in value]
                elif isinstance(value, (float, np.floating)) and np.isnan(value):
                    trace[key] = None
        
        # Convert to JSON-serializable format
        serializable_fig_dict = convert_to_serializable(fig_dict)
        
        component = {
            "type": "plot",
            "id": id,
            "data": {
                "data": serializable_fig_dict.get("data", []),
                "layout": serializable_fig_dict.get("layout", {}),
                "config": {
                    "responsive": True,
                    "displayModeBar": True,
                    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                    "displaylogo": False
                }
            }
        }
        
        # Verify JSON serialization
        json.dumps(component)
        
        logger.debug(f"Plot data created successfully for id {id}")
        _rendered_html.append(component)
        return component
        
    except Exception as e:
        logger.error(f"Error creating plot: {str(e)}", exc_info=True)
        error_component = {
            "type": "plot",
            "id": id,
            "error": f"Failed to create plot: {str(e)}"
        }
        _rendered_html.append(error_component)
        return error_component

def table(data, title=None):
    """Create a table component that renders data using TableViewerWidget.
    
    Args:
        data: List of dictionaries or pandas DataFrame to display
        title: Optional title for the table
    """
    id = generate_id("table")
    logger.debug(f"Creating table component with id {id}")
    
    try:
        # Convert pandas DataFrame to list of dictionaries if needed
        if hasattr(data, 'to_dict'):
            # Reset index and drop it to avoid index column in output
            if isinstance(data, pd.DataFrame):
                data = data.reset_index(drop=True)
            data = data.to_dict('records')
        
        # Ensure data is a list
        if not isinstance(data, list):
            data = [data] if data else []
        
        # Convert each row to ensure JSON serialization
        processed_data = []
        for row in data:
            if isinstance(row, dict):
                processed_row = {}
                for key, value in row.items():
                    # Convert key to string to ensure it's serializable
                    key_str = str(key)
                    # Handle special cases and convert value
                    if pd.isna(value):
                        processed_row[key_str] = None
                    elif isinstance(value, (pd.Timestamp, pd.DatetimeTZDtype)):
                        processed_row[key_str] = str(value)
                    elif isinstance(value, (np.integer, np.floating)):
                        processed_row[key_str] = value.item()
                    elif isinstance(value, (list, np.ndarray)):
                        processed_row[key_str] = convert_to_serializable(value)
                    else:
                        try:
                            # Try to serialize to test if it's JSON-compatible
                            json.dumps(value)
                            processed_row[key_str] = value
                        except:
                            # If serialization fails, convert to string
                            processed_row[key_str] = str(value)
                processed_data.append(processed_row)
            else:
                # If row is not a dict, convert it to a simple dict
                processed_data.append({"value": str(row)})
        
        component = {
            "type": "table",
            "id": id,
            "data": processed_data,
            "title": str(title) if title is not None else None
        }
        
        # Verify JSON serialization before returning
        json.dumps(component)
        
        logger.debug(f"Created table component: {component}")
        _rendered_html.append(component)
        return component
        
    except Exception as e:
        logger.error(f"Error creating table component: {str(e)}")
        error_component = {
            "type": "table",
            "id": id,
            "data": [],
            "title": f"Error: {str(e)}"
        }
        _rendered_html.append(error_component)
        return error_component