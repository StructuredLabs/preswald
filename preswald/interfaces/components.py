# Standard Library
import asyncio
import hashlib
import io
import json
import logging
import uuid
from typing import Dict, List, Optional

# Third-Party
import fastplotlib as fplt
import msgpack
import numpy as np
import pandas as pd
from PIL import Image

# Internal
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
    component_id = generate_id_by_label("checkbox", label)

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

This component uses Fastplotlib and WGPU for offscreen GPU rendering of scatter plots,
and streams the resulting PNG image to the frontend over a WebSocket connection.

It is optimized for large datasets and avoids unnecessary re-rendering by hashing the
input data and skipping image generation if the data hasn't changed.

Args:
    label (str): A descriptive label for the plot. Used to generate a stable component ID.
    data (dict): The structured data to be plotted. Expected keys:
        - "x" (list or np.ndarray): x-axis coordinates.
        - "y" (list or np.ndarray): y-axis coordinates.
        - "color" (optional): A list of string labels used to assign colors to points.
          - Colors are assigned from a fixed RGBA palette based on label uniqueness and order.
          - This does not support direct RGBA arrays or named color strings at this time.
        - "client_id" (str): WebSocket session ID used to route the rendered image to the client.
    size (float, optional): Layout width of the component in a row (0.0-1.0). Defaults to 1.0.

Returns:
    str: A stable component ID referencing the rendered Fastplotlib figure.

Notes:
    - Colors are currently assigned from a fixed palette using label-based mapping.
    - PNGs are encoded and sent via WebSocket using MessagePack.
    - Rendering is skipped if input data has not changed (SHA-256 hash check).
    - The component currently renders static images and does not support zoom or tooltips.
    """
    service = PreswaldService.get_instance()

    default_color_palette = [
        [1.0, 0.0, 0.0, 1.0],  # Red
        [0.0, 1.0, 0.0, 1.0],  # Green
        [0.0, 0.0, 1.0, 1.0],  # Blue
        [1.0, 1.0, 0.0, 1.0],  # Yellow
        [1.0, 0.0, 1.0, 1.0],  # Magenta
        [0.0, 1.0, 1.0, 1.0],  # Cyan
    ]

    # hash input data early and use hash to avoid unecessary image
    # rendering
    hashable_data = {
        "x": data.get("x", []),
        "y": data.get("y", []),
        "color": data.get("color", None),
        "label": label,
        "size": size
    }
    data_hash = hashlib.sha256(msgpack.packb(hashable_data)).hexdigest()

    component_id = generate_id_by_label("fastplotlib", label)
    component = {
        "id": component_id,
        "type": "fastplotlib_component",
        "label": label,
        "size": size,
        "format": "websocket-png",
        "value": None,
        "hash": data_hash[:8]
    }

    # skip if data hash has not changed
    if data_hash == service.get_component_state(f"{component_id}_img_hash"):
        service.append_component(component)
        return component_id

    x = np.asarray(data.get("x", []), dtype=np.float32)
    y = np.asarray(data.get("y", []), dtype=np.float32)
    if x.size == 0 or y.size == 0:
        raise ValueError("Fastplotlib requires non-empty 'x' and 'y' data.")

    points = np.column_stack((x, y))

    # map input labels to RGBA values using a fixed color palette
    # if labels are provided, assign distinct colors; otherwise default to blue
    color_input = data.get("color", None)
    if isinstance(color_input, (np.ndarray, list)):
        color_input = np.asarray(color_input).tolist()
        unique_labels = list(dict.fromkeys(color_input))
        label_to_color = {
            label: default_color_palette[i % len(default_color_palette)]
            for i, label in enumerate(unique_labels)
        }
        rgba_color = np.array([label_to_color[label] for label in color_input], dtype=np.float32)
    else:
        rgba_color = np.array([[0.0, 0.0, 1.0, 1.0]] * points.shape[0], dtype=np.float32)

    # set up Fastplotlib figure with offscreen canvas to avoid opening a GUI window
    # add a scatter plot to the first subplot using the computed coordinates and colors
    fig = fplt.Figure(size=(700, 560), canvas="offscreen")
    subplot = fig[0, 0]
    subplot.add_scatter(data=points, sizes=6, alpha=0.7, colors=rgba_color)
    fig.show()

    # manually trigger the renderer to ensure the scene is fully drawn before exporting
    try:
        fig.renderer.render(subplot.scene, fig.cameras[0, 0])
    except Exception as e:
        logger.error(f"Manual render failed: {e}")
        return "Render failed"

    # attempt to export the rendered scene to a NumPy array representing the image
    try:
        img_array = fig.export_numpy(rgb=True)
    except Exception as e:
        logger.error(f"fastplotlib export failed: {e}")
        # if export fails, try forcing a draw and flush to get the rendered image
        fig.canvas.request_draw()
        fig.renderer.flush()
        img_array = fig.canvas.draw()

    # convert the NumPy image array into a PNG byte buffer in memory
    img_buf = io.BytesIO()
    Image.fromarray(img_array).save(img_buf, format="PNG")
    img_buf.seek(0)
    png_bytes = img_buf.read()

    # send the PNG image over the WebSocket to the corresponding client
    client_id = data.get("client_id", None)
    if client_id:
        websocket = service.websocket_connections.get(client_id)
        if websocket:
            async def send_and_update(packed_msg):
                try:
                    await websocket.send_bytes(packed_msg)
                    await service.handle_client_message(client_id, {
                        "type": "component_update",
                        "states": {
                            f"{component_id}_img_hash": data_hash
                        }
                    })
                    logger.debug(f"✅ Sent Fastplotlib image via WebSocket (MessagePack) to client {client_id}")
                except Exception as e:
                    logger.error(f"WebSocket send failed: {e}")

            packed_msg = msgpack.packb({
                "type": "image_update",
                "component_id": component_id,
                "format": "png",
                "label": label,
                "size": size,
                "data": png_bytes
            })
            asyncio.create_task(send_and_update(packed_msg))  # noqa: RUF006

        else:
            logger.warning(f"No active WebSocket found for client_id={client_id}")

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

    component_id = generate_id_by_label("selectbox", label)
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
    component_id = generate_id_by_label("slider", label)

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
    component_id = generate_id_by_label("text_input", label)

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

def generate_id_by_label(prefix: str, label: str) -> str:
    """
    Generate a deterministic component ID based on a label string.

    Useful for components like Fastplotlib or Slider where the same label should result
    in the same component ID across rerenders.

    Args:
        prefix (str): The component type prefix, e.g. 'slider' or 'fastplotlib'.
        label (str): The label to hash and include in the ID.

    Returns:
        str: A stable ID like 'slider-ab12cd34'.
    """
    if not label:
        return generate_id(prefix)
    hashed = hashlib.md5(label.lower().encode()).hexdigest()[:8]
    return f"{prefix}-{hashed}"
