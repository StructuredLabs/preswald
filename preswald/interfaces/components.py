import hashlib
import json
import logging
import uuid
import base64
import io

import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from preswald.engine.service import PreswaldService

# Configure logging
logger = logging.getLogger(__name__)


def generate_id(prefix="component"):
    """Generate a unique ID for a component."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def checkbox(label, default=False, size=1.0) -> bool:
    """Create a checkbox component with consistent ID based on label."""
    service = PreswaldService.get_instance()

    # Create a consistent ID based on the label
    component_id = f"checkbox-{hashlib.md5(label.encode()).hexdigest()[:8]}"

    # Get current state or use default
    current_value = service.get_component_state(component_id)
    if current_value is None:
        current_value = default

    logger.debug(f"Creating checkbox component with id {component_id}, label: {label}")
    component = {
        "type": "checkbox",
        "id": component_id,
        "label": label,
        "value": current_value,
        "size": size,
    }
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return current_value


def slider(
    label: str,
    min_val: float = 0.0,
    max_val: float = 100.0,
    step: float = 1.0,
    default: float = None,
    size: float = 1.0,
) -> float:
    """Create a slider component with consistent ID based on label"""
    service = PreswaldService.get_instance()

    # Create a consistent ID based on the label
    component_id = f"slider-{hashlib.md5(label.encode()).hexdigest()[:8]}"

    # Get current state or use default
    current_value = service.get_component_state(component_id)
    if current_value is None:
        current_value = default if default is not None else min_val

    component = {
        "type": "slider",
        "id": component_id,
        "label": label,
        "min": min_val,
        "max": max_val,
        "step": step,
        "value": current_value,
        "size": size,
    }

    service.append_component(component)
    return current_value


def button(label, size=1.0):
    """Create a button component."""
    service = PreswaldService.get_instance()
    id = generate_id("button")
    logger.debug(f"Creating button component with id {id}, label: {label}")
    component = {"type": "button", "id": id, "label": label, "size": size}
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return component


def selectbox(label, options, default=None, size=1.0):
    """Create a select component with consistent ID based on label."""
    service = PreswaldService.get_instance()

    component_id = f"selectbox-{hashlib.md5(label.encode()).hexdigest()[:8]}"
    current_value = service.get_component_state(component_id)
    if current_value is None:
        current_value = default if default is not None else (options[0] if options else None)

    component = {
        "type": "selectbox",
        "id": component_id,
        "label": label,
        "options": options,
        "value": current_value,
        "size": size,
    }
    service.append_component(component)
    return current_value


def text_input(label, placeholder="", size=1.0) -> str:
    """Create a text input component with consistent ID based on label."""
    service = PreswaldService.get_instance()

    # Create a consistent ID based on the label
    component_id = f"text_input-{hashlib.md5(label.encode()).hexdigest()[:8]}"

    # Get current state or use default
    current_value = service.get_component_state(component_id)
    if current_value is None:
        current_value = ""

    logger.debug(
        f"Creating text input component with id {component_id}, label: {label}"
    )
    component = {
        "type": "text_input",
        "id": component_id,
        "label": label,
        "placeholder": placeholder,
        "value": current_value,
        "size": size,
    }
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return current_value


def progress(label, value=0, size=1.0):
    """Create a progress component."""
    service = PreswaldService.get_instance()

    id = generate_id("progress")
    logger.debug(f"Creating progress component with id {id}, label: {label}")
    component = {
        "type": "progress",
        "id": id,
        "label": label,
        "value": value,
        "size": size,
    }
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return component


def spinner(label, size=1.0):
    """Create a spinner component."""
    service = PreswaldService.get_instance()
    id = generate_id("spinner")
    logger.debug(f"Creating spinner component with id {id}, label: {label}")
    component = {"type": "spinner", "id": id, "label": label, "size": size}
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return component


def alert(message, level="info", size=1.0):
    """Create an alert component."""
    service = PreswaldService.get_instance()

    id = generate_id("alert")
    logger.debug(f"Creating alert component with id {id}, message: {message}")
    component = {
        "type": "alert",
        "id": id,
        "message": message,
        "level": level,
        "size": size,
    }
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return component


def image(src, alt="Image", size=1.0):
    """Create an image component."""
    service = PreswaldService.get_instance()
    id = generate_id("image")
    logger.debug(f"Creating image component with id {id}, src: {src}")
    component = {"type": "image", "id": id, "src": src, "alt": alt, "size": size}
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return component


def text(markdown_str, size=1.0) -> str:
    """Create a text/markdown component."""
    service = PreswaldService.get_instance()
    id = generate_id("text")
    logger.debug(f"Creating text component with id {id}")
    component = {
        "type": "text",
        "id": id,
        "markdown": markdown_str,
        "value": markdown_str,
        "size": size,
    }
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return markdown_str


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


def plotly(fig, size=1.0):
    """
    Render a Plotly figure.

    Args:
        fig: A Plotly figure object.
    """
    service = PreswaldService.get_instance()
    try:
        import time

        start_time = time.time()
        logger.debug(f"[PLOTLY] Starting plotly render")

        id = generate_id("plot")
        logger.debug(f"[PLOTLY] Created plot component with id {id}")

        # Optimize the figure for web rendering
        optimize_start = time.time()

        # Reduce precision of numeric values
        for trace in fig.data:
            for attr in ["x", "y", "z", "lat", "lon"]:
                if hasattr(trace, attr):
                    values = getattr(trace, attr)
                    if isinstance(values, (list, np.ndarray)):
                        if np.issubdtype(np.array(values).dtype, np.floating):
                            setattr(trace, attr, np.round(values, decimals=4))

            # Optimize marker sizes
            if hasattr(trace, "marker") and hasattr(trace.marker, "size"):
                if isinstance(trace.marker.size, (list, np.ndarray)):
                    # Scale marker sizes to a reasonable range
                    sizes = np.array(trace.marker.size)
                    if len(sizes) > 0:
                        min_size, max_size = (
                            5,
                            20,
                        )  # Reasonable size range for web rendering
                        with np.errstate(divide='ignore', invalid='ignore'):
                            scaled_sizes = (sizes / max_size) * max_size
                            scaled_sizes = np.nan_to_num(scaled_sizes, nan=0.0, posinf=0.0, neginf=0.0)

                        # Ensure there's a minimum size if needed
                        scaled_sizes = np.clip(scaled_sizes, 1, max_size)

                        trace.marker.size = scaled_sizes.tolist()

        # Optimize layout
        if hasattr(fig, "layout"):
            # Set reasonable margins
            fig.update_layout(margin=dict(l=50, r=50, t=50, b=50), autosize=True)

            # Optimize font sizes
            fig.update_layout(font=dict(size=12), title=dict(font=dict(size=14)))

        logger.debug(
            f"[PLOTLY] Figure optimization took {time.time() - optimize_start:.3f}s"
        )

        # Convert the figure to JSON-serializable format
        fig_dict_start = time.time()
        fig_dict = fig.to_dict()
        logger.debug(
            f"[PLOTLY] Figure to dict conversion took {time.time() - fig_dict_start:.3f}s"
        )

        # Clean up any NaN values in the data
        clean_start = time.time()
        for trace in fig_dict.get("data", []):
            if isinstance(trace.get("marker"), dict):
                marker = trace["marker"]
                if "sizeref" in marker and (
                    isinstance(marker["sizeref"], float) and np.isnan(marker["sizeref"])
                ):
                    marker["sizeref"] = None

            # Clean up other potential NaN values
            for key, value in trace.items():
                if isinstance(value, (list, np.ndarray)):
                    trace[key] = [
                        (
                            None
                            if isinstance(x, (float, np.floating)) and np.isnan(x)
                            else x
                        )
                        for x in value
                    ]
                elif isinstance(value, (float, np.floating)) and np.isnan(value):
                    trace[key] = None
        logger.debug(f"[PLOTLY] NaN cleanup took {time.time() - clean_start:.3f}s")

        # Convert to JSON-serializable format
        serialize_start = time.time()
        serializable_fig_dict = convert_to_serializable(fig_dict)
        logger.debug(
            f"[PLOTLY] Serialization took {time.time() - serialize_start:.3f}s"
        )

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
                    "displaylogo": False,
                    "scrollZoom": True,  # Enable scroll zoom for better interaction
                    "showTips": False,  # Disable hover tips for better performance
                },
            },
            "size": size,
        }

        # Verify JSON serialization
        json_start = time.time()
        json.dumps(component)
        logger.debug(f"[PLOTLY] JSON verification took {time.time() - json_start:.3f}s")

        logger.debug(f"[PLOTLY] Plot data created successfully for id {id}")
        logger.debug(
            f"[PLOTLY] Total plotly render took {time.time() - start_time:.3f}s"
        )
        service.append_component(component)
        return component

    except Exception as e:
        logger.error(f"[PLOTLY] Error creating plot: {str(e)}", exc_info=True)
        error_component = {
            "type": "plot",
            "id": id,
            "error": f"Failed to create plot: {str(e)}",
        }
        service.append_component(error_component)
        return error_component


def table(data, title=None):
    """Create a table component that renders data using TableViewerWidget.

    Args:
        data: List of dictionaries or pandas DataFrame to display
        title: Optional title for the table
    """
    id = generate_id("table")
    logger.debug(f"Creating table component with id {id}")
    service = PreswaldService.get_instance()

    try:
        # Convert pandas DataFrame to list of dictionaries if needed
        if hasattr(data, "to_dict"):
            # Reset index and drop it to avoid index column in output
            if isinstance(data, pd.DataFrame):
                data = data.reset_index(drop=True)
            data = data.to_dict("records")

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
            "title": str(title) if title is not None else None,
        }

        # Verify JSON serialization before returning
        json.dumps(component)

        logger.debug(f"Created table component: {component}")
        service.append_component(component)
        return component

    except Exception as e:
        logger.error(f"Error creating table component: {str(e)}")
        error_component = {
            "type": "table",
            "id": id,
            "data": [],
            "title": f"Error: {str(e)}",
        }
        service.append_component(error_component)
        return error_component


def workflow_dag(workflow, title="Workflow Dependency Graph"):
    """
    Render the workflow's DAG visualization.

    Args:
        workflow: The workflow object to visualize
        title: Optional title for the visualization
    """
    service = PreswaldService.get_instance()
    try:
        from .workflow import WorkflowAnalyzer

        analyzer = WorkflowAnalyzer(workflow)
        analyzer.build_graph()  # Ensure graph is built

        # Get node data
        nodes_data = []
        for node, data in analyzer.graph.nodes(data=True):
            nodes_data.append(
                {
                    "name": node,
                    "status": data["status"],
                    "execution_time": data["execution_time"],
                    "attempts": data["attempts"],
                    "error": data["error"],
                    "dependencies": data["dependencies"],
                    "force_recompute": data["force_recompute"],
                }
            )

        # Create the component with the correct type and data structure
        id = generate_id("dag")
        component = {
            "type": "dag",  # Changed from "plot" to "dag"
            "id": id,
            "data": {
                "data": [
                    {
                        "type": "scatter",
                        "customdata": nodes_data,
                        "node": {"positions": []},  # Will be calculated by react-flow
                    }
                ],
                "layout": {"title": {"text": title}, "showlegend": True},
            },
        }

        logger.debug(f"[WORKFLOW_DAG] Created DAG component with id {id}")
        service.append_component(component)
        return component

    except Exception as e:
        logger.error(
            f"[WORKFLOW_DAG] Error creating DAG visualization: {str(e)}", exc_info=True
        )
        error_component = {
            "type": "dag",  # Changed from "plot" to "dag"
            "id": generate_id("dag"),
            "error": f"Failed to create DAG visualization: {str(e)}",
        }
        service.append_component(error_component)
        return error_component


# Add separator component function
def separator():
    """Create a separator component that forces a new row."""
    service = PreswaldService.get_instance()
    component = {"type": "separator", "id": str(uuid.uuid4())}
    service.append_component(component)
    return component


class MatplotlibWrapper:
    """
    A wrapper class for matplotlib functionality in Preswald.
    """
    def __init__(self):
        import matplotlib.pyplot as plt
        self.plt = plt
        self.format = 'png'  # default format
        
    def __call__(self, fig, label=None, format='png'): 
        """
        Original matplotlib function to display a figure
        
        Args:
            fig: matplotlib.figure.Figure object
            format: 'png' or 'svg' (default: 'png')
        """
        if not isinstance(fig, Figure):
            raise TypeError("Expected matplotlib.figure.Figure, got {}".format(type(fig)))
        
        if format not in ['png', 'svg']:
            raise ValueError("Format must be 'png' or 'svg'")
            
        service = PreswaldService.get_instance()
        buf = io.BytesIO()
        
        # Set figure DPI for better quality
        if format == 'svg':
            fig.savefig(buf, format=format, bbox_inches='tight')
        else:
            fig.savefig(buf, format=format, bbox_inches='tight', dpi=100)
            
        buf.seek(0)
        
        # For SVG, decode as UTF-8 string first
        if format == 'svg':
            img_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        else:
            img_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        component = {
            "type": "matplotlib", 
            "data": { 
                "image": img_data,
                "format": format
            }
        }
        service.append_component(component)
        return component
        
    def plot(self, *args, format='png', label=None, **kwargs):
        """
        Create a line plot, similar to matplotlib.pyplot.plot()
        
        Args:
            *args: Arguments passed to plt.plot()
            format: 'png' or 'svg' (default: 'png')
            **kwargs: Keyword arguments passed to plt.plot()
        """
        if format not in ['png', 'svg']:
            raise ValueError("Format must be 'png' or 'svg'")
            
        # Create a new figure if one doesn't exist
        if not self.plt.get_fignums():
            self.plt.figure(figsize=(10, 6))
            
        # Create the plot
        self.plt.plot(*args, label=label, **kwargs)
        
        # Return the component
        return self(self.plt.gcf(), label=label, format=format)

# Replace the function with an instance of the wrapper class
matplotlib = MatplotlibWrapper()
