import base64
import hashlib
import io
import json
import logging
import uuid
from typing import Dict, List, Optional

import fastplotlib as fplt
import numpy as np
import pandas as pd
from PIL import Image

from preswald.engine.service import PreswaldService
from preswald.interfaces.workflow import Workflow


# Configure logging
logger = logging.getLogger(__name__)

# NOTE to Developers: Please keep the components organized alphabetically

# Components


def alert(message: str, level: str = "info", size: float = 1.0) -> str:
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
    return message


# TODO: Add button functionality
def button(label: str, size: float = 1.0):
    """Create a button component."""
    service = PreswaldService.get_instance()
    id = generate_id("button")
    logger.debug(f"Creating button component with id {id}, label: {label}")
    component = {"type": "button", "id": id, "label": label, "size": size}
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return component


def checkbox(label: str, default: bool = False, size: float = 1.0) -> bool:
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

def fastplotlib(
    label: str,
    data: dict,
    size: float = 1.0
) -> str:
    """
    Create a Fastplotlib component for high-performance GPU-accelerated plotting.

    Fastplotlib leverages GPU rendering via WGPU to generate real-time, interactive visualizations.
    This component allows users to plot structured numerical data such as scatter plots.

    Args:
        label (str): A descriptive label for the plot.
        data (dict): The structured data to be plotted. Expected keys:
            - "x" (list or np.ndarray): x-axis coordinates.
            - "y" (list or np.ndarray): y-axis coordinates.
            - "color" (optional): A list of labels (e.g., species names) to assign different colors to points.
              - If a list of labels is provided, a small default RGBA color palette is cycled.
              - If omitted or invalid, all points are rendered in blue.
        size (float, optional): The size scaling factor for the rendered image component. Defaults to 1.0.

    Returns:
        str: A unique component ID referencing the rendered Fastplotlib figure.

    Note:
        Colors are currently cycled from a fixed palette. For more fine-grained control,
        consider extending this component to accept RGBA color arrays or named colors.
    """

    service = PreswaldService.get_instance()

    # create the figure with offscreen rendering.
    # without cavas="offscreen" fastplotlib will attempt to open a
    # window on the server for rendering
    fig = fplt.Figure(size=(700, 560), canvas="offscreen")

    # extract x and y values from provided data
    x = np.asarray(data.get("x", [])).astype(np.float32)
    y = np.asarray(data.get("y", [])).astype(np.float32)

    if x.size == 0 or y.size == 0:
        raise ValueError("Fastplotlib requires non-empty 'x' and 'y' data.")

    # combine x and y into a single NumPy array with shape (N, 2)
    points = np.column_stack((x, y))

    # define a small palette of distinct RGBA colors normalized to [0, 1]
    default_color_palette = [
        [1.0, 0.0, 0.0, 1.0],  # Red
        [0.0, 1.0, 0.0, 1.0],  # Green
        [0.0, 0.0, 1.0, 1.0],  # Blue
        [1.0, 1.0, 0.0, 1.0],  # Yellow
        [1.0, 0.0, 1.0, 1.0],  # Magenta
        [0.0, 1.0, 1.0, 1.0],  # Cyan
    ]

    color_input = data.get("color", None)
    if isinstance(color_input, (np.ndarray, list)):
        color_input = np.asarray(color_input).tolist()
        unique_labels = list(dict.fromkeys(color_input))  # Preserve order
        label_to_color = {
            label: default_color_palette[i % len(default_color_palette)]
            for i, label in enumerate(unique_labels)
        }
        rgba_color = np.array([label_to_color[label] for label in color_input], dtype=np.float32)
    else:
        # fall back to default blue
        rgba_color = np.array([[0.0, 0.0, 1.0, 1.0]] * points.shape[0], dtype=np.float32)

    logger.info(f"✅ Debug: Color shape = {rgba_color.shape}")

    # create scatter plot graphic using add_scatter method
    subplot = fig[0, 0]  # Access the first subplot in the figure
    subplot.add_scatter(data=points, sizes=6, alpha=0.7, colors=rgba_color)

    # show the figure to trigger the rendering
    fig.show()

    # force rendering step before exporting
    try:
        # manually trigger render for the scene and camera
        fig.renderer.render(subplot.scene, fig.cameras[0, 0])
    except Exception as e:
        logger.error(f"Manual render failed: {e}")
        return "Render failed"

    # now, we can export the figure
    try:
        img_array = fig.export_numpy(rgb=True)
    except Exception as e:
        logger.error(f"fastplotlib export failed: {e}")
        logger.warning("attempting manual render and capture...")
        fig.canvas.request_draw()
        fig.renderer.flush()
        img_array = fig.canvas.draw()

    # convert the NumPy array to an image buffer (PNG format)
    img_buf = io.BytesIO()
    Image.fromarray(img_array).save(img_buf, format="PNG")
    img_buf.seek(0)

    # convert to base64 for embedding in the component
    img_base64 = base64.b64encode(img_buf.read()).decode()

    # create the component ID and return
    component_id = generate_id("fastplotlib")
    component = {
        "type": "fastplotlib_component",
        "id": component_id,
        "label": label,
        "src": f"data:image/png;base64,{img_base64}",
        "size": size,
    }

    service.append_component(component)
    return component_id

# TODO: requires testing
def image(src, alt="Image", size=1.0):
    """Create an image component."""
    service = PreswaldService.get_instance()
    id = generate_id("image")
    logger.debug(f"Creating image component with id {id}, src: {src}")
    component = {"type": "image", "id": id, "src": src, "alt": alt, "size": size}
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return component


def plotly(fig, size: float = 1.0) -> Dict:  # noqa: C901
    """
    Render a Plotly figure.

    Args:
        fig: A Plotly figure object.
    """
    service = PreswaldService.get_instance()
    try:
        import time

        start_time = time.time()
        logger.debug("[PLOTLY] Starting plotly render")

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
                        _min_size, max_size = (
                            5,
                            20,
                        )  # Reasonable size range for web rendering
                        with np.errstate(divide="ignore", invalid="ignore"):
                            scaled_sizes = (sizes / max_size) * max_size
                            scaled_sizes = np.nan_to_num(
                                scaled_sizes, nan=0.0, posinf=0.0, neginf=0.0
                            )

                        # Ensure there's a minimum size if needed
                        scaled_sizes = np.clip(scaled_sizes, 1, max_size)

                        trace.marker.size = scaled_sizes.tolist()

        # Optimize layout
        if hasattr(fig, "layout"):
            # Set reasonable margins
            fig.update_layout(
                margin={"l": 50, "r": 50, "t": 50, "b": 50}, autosize=True
            )

            # Optimize font sizes
            fig.update_layout(font={"size": 12}, title={"font": {"size": 14}})

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
        logger.error(f"[PLOTLY] Error creating plot: {e!s}", exc_info=True)
        error_component = {
            "type": "plot",
            "id": id,
            "error": f"Failed to create plot: {e!s}",
        }
        service.append_component(error_component)
        return error_component


def progress(label: str, value: float = 0.0, size: float = 1.0) -> float:
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
    return value


def selectbox(
    label: str, options: List[str], default: Optional[str] = None, size: float = 1.0
) -> str:
    """Create a select component with consistent ID based on label."""
    service = PreswaldService.get_instance()

    component_id = f"selectbox-{hashlib.md5(label.encode()).hexdigest()[:8]}"
    current_value = service.get_component_state(component_id)
    if current_value is None:
        current_value = (
            default if default is not None else (options[0] if options else None)
        )

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


def separator() -> Dict:
    """Create a separator component that forces a new row."""
    service = PreswaldService.get_instance()
    component = {"type": "separator", "id": str(uuid.uuid4())}
    service.append_component(component)
    return component


def slider(
    label: str,
    min_val: float = 0.0,
    max_val: float = 100.0,
    step: float = 1.0,
    default: Optional[float] = None,
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


# TODO: requires testing
def spinner(label: str, size: float = 1.0):
    """Create a spinner component."""
    service = PreswaldService.get_instance()
    id = generate_id("spinner")
    logger.debug(f"Creating spinner component with id {id}, label: {label}")
    component = {"type": "spinner", "id": id, "label": label, "size": size}
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return component


def sidebar(defaultopen: bool):
    """Create a sidebar component."""
    service = PreswaldService.get_instance()
    id = generate_id("sidebar")
    logger.debug(f"Creating sidebar component with id {id}")
    component = {"type": "sidebar", "id": id, "defaultopen": defaultopen}
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return component


def table(  # noqa: C901
    data: pd.DataFrame, title: Optional[str] = None, limit: Optional[int] = None
) -> Dict:
    """Create a table component that renders data using TableViewerWidget.

    Args:
        data: Pandas DataFrame or list of dictionaries to display
        title: Optional title for the table

    Returns:
        Dict: Component metadata and processed data
    """
    id = generate_id("table")
    logger.debug(f"Creating table component with id {id}")
    service = PreswaldService.get_instance()

    try:
        # Convert pandas DataFrame to list of dictionaries if needed
        if hasattr(data, "to_dict"):
            if isinstance(data, pd.DataFrame):
                data = data.reset_index(drop=True)
                if limit is not None:
                    data = data.head(limit)
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
                        except:  # noqa: E722
                            # If serialization fails, convert to string
                            processed_row[key_str] = str(value)
                processed_data.append(processed_row)
            else:
                # If row is not a dict, convert it to a simple dict
                processed_data.append({"value": str(row)})

        # Create the component structure
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
        logger.error(f"Error creating table component: {e!s}")
        error_component = {
            "type": "table",
            "id": id,
            "data": [],
            "title": f"Error: {e!s}",
        }
        service.append_component(error_component)
        return error_component


def text(markdown_str: str, size: float = 1.0) -> str:
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


def text_input(label: str, placeholder: str = "", size: float = 1.0) -> str:
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


def workflow_dag(workflow: Workflow, title: str = "Workflow Dependency Graph") -> Dict:
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
            f"[WORKFLOW_DAG] Error creating DAG visualization: {e!s}", exc_info=True
        )
        error_component = {
            "type": "dag",  # Changed from "plot" to "dag"
            "id": generate_id("dag"),
            "error": f"Failed to create DAG visualization: {e!s}",
        }
        service.append_component(error_component)
        return error_component

# Helpers


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


def generate_id(prefix: str = "component") -> str:
    """Generate a unique ID for a component."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"
