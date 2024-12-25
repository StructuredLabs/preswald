import uuid
from preswald.core import _rendered_html, get_component_state
import logging
import numpy as np
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_id(prefix="component"):
    """Generate a unique ID for a component."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def checkbox(label, default=False):
    """Create a checkbox component."""
    id = generate_id("checkbox")
    logger.debug(f"Creating checkbox component with id {id}, label: {label}")
    component = {
        "type": "checkbox",
        "id": id,
        "label": label,
        "value": get_component_state(id, default)
    }
    logger.debug(f"Created component: {component}")
    _rendered_html.append(component)
    return component

def slider(label, min_val=0, max_val=100, step=1, default=50):
    """Create a slider component."""
    id = generate_id("slider")
    logger.debug(f"Creating slider component with id {id}, label: {label}")
    component = {
        "type": "slider",
        "id": id,
        "label": label,
        "min": min_val,
        "max": max_val,
        "step": step,
        "value": get_component_state(id, default)
    }
    logger.debug(f"Created component: {component}")
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
    """Create a select component."""
    id = generate_id("selectbox")
    logger.debug(f"Creating selectbox component with id {id}, label: {label}")
    component = {
        "type": "selectbox",
        "id": id,
        "label": label,
        "options": options,
        "value": get_component_state(id, default or options[0] if options else None)
    }
    logger.debug(f"Created component: {component}")
    _rendered_html.append(component)
    return component

def text_input(label, placeholder=""):
    """Create a text input component."""
    id = generate_id("text_input")
    logger.debug(f"Creating text input component with id {id}, label: {label}")
    component = {
        "type": "text_input",
        "id": id,
        "label": label,
        "placeholder": placeholder,
        "value": get_component_state(id, "")
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
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, np.generic):
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
        
        # Convert the figure to JSON-serializable format first
        fig_dict = fig.to_dict()
        serializable_fig_dict = convert_to_serializable(fig_dict)
        
        # Test JSON serialization before proceeding
        json.dumps(serializable_fig_dict)
        
        # Only generate HTML after ensuring data is serializable
        html = fig.to_html(full_html=False, include_plotlyjs="cdn")
        
        # Get the figure's data, layout and config
        data = {
            "type": "plot",
            "id": id,
            "content": html,  # HTML version for backward compatibility
            "data": {
                "data": serializable_fig_dict["data"],  # The traces in JSON-serializable format
                "layout": serializable_fig_dict["layout"],  # The layout in JSON-serializable format
                "config": {  # Enhanced config for better UX
                    "responsive": True,
                    "displayModeBar": True,
                    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                    "displaylogo": False
                }
            }
        }
        
        logger.debug(f"Plot data created successfully for id {id}")
        _rendered_html.append(data)
        return data
        
    except Exception as e:
        logger.error(f"Error creating plot: {str(e)}", exc_info=True)
        error_component = {
            "type": "plot",
            "id": id,
            "error": f"Failed to create plot: {str(e)}"
        }
        _rendered_html.append(error_component)
        return error_component