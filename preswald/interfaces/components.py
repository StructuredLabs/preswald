# Standard Library
import asyncio
import base64
import hashlib
import io
import json
import logging
import uuid
from typing import Dict, List, Optional, Union

# Third-Party
import fastplotlib as fplt
import matplotlib.pyplot as plt
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


def chat(source: str, table: Optional[str] = None) -> Dict:
    """Create a chat component to chat with data source"""
    service = PreswaldService.get_instance()

    # Create a consistent ID based on the source
    component_id = f"chat-{hashlib.md5(str(source).encode()).hexdigest()[:8]}"

    # Get current state or initialize empty
    current_state = service.get_component_state(component_id)
    if current_state is None:
        current_state = {"messages": [], "source": source}

    # Get dataframe from source
    df = (
        service.data_manager.get_df(source)
        if table is None
        else service.data_manager.get_df(source, table)
    )

    # Convert DataFrame to serializable format
    serializable_data = None
    if df is not None:
        records = df.to_dict("records")
        # Handle timestamp fields before general serialization
        processed_records = []
        for record in records:
            processed_record = {}
            for key, value in record.items():
                if isinstance(value, (pd.Timestamp, pd.NaT.__class__)):
                    processed_record[key] = (
                        value.isoformat() if not pd.isna(value) else None
                    )
                else:
                    processed_record[key] = value
            processed_records.append(processed_record)
        serializable_data = convert_to_serializable(processed_records)

    logger.debug(f"Creating chat component with id {component_id}, source: {source}")
    component = {
        "type": "chat",
        "id": component_id,
        "state": {
            "messages": current_state.get("messages", []),
        },
        "config": {
            "source": source,
            "data": serializable_data,
        },
    }

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


def fastplotlib(fig: fplt.Figure, size: float = 1.0) -> str:
    """
    Render a Fastplotlib figure and asynchronously stream the resulting image to the frontend.

    This component leverages Fastplotlib's GPU-accelerated offscreen rendering capabilities.
    Rendering and transmission are triggered only when the figure state or the client changes,
    ensuring efficient updates. The rendered image is encoded as a PNG and sent to the frontend
    via WebSocket using MessagePack.

    Args:
        fig (fplt.Figure): A configured Fastplotlib figure ready to be rendered.
        size (float, optional): Width of the rendered component relative to its container (0.0-1.0).
                                Defaults to 1.0.

    Returns:
        str: A deterministic component ID used to reference the figure on the frontend.

    Notes:
        - The figure must have '_label' and '_client_id' attributes set externally.
        - Rendering occurs asynchronously if the figure state or client_id changes.
        - If client_id is not provided, a warning is logged and no rendering task is triggered.
    """
    service = PreswaldService.get_instance()

    label = getattr(fig, "_label", "fastplotlib")
    component_id = generate_id_by_label("fastplotlib", label)

    try:
        state = fig.get_state()
    except Exception:
        state = label

    # hash input data early and use hash to avoid unnecessary rendering
    client_id = getattr(fig, "_client_id", None)
    hashable_data = {
        "client_id": client_id,
        "state": state,
        "label": label,
        "size": size,
    }
    data_hash = hashlib.sha256(msgpack.packb(hashable_data)).hexdigest()

    component = {
        "id": component_id,
        "type": "fastplotlib_component",
        "label": label,
        "size": size,
        "format": "websocket-png",
        "value": None,
        "hash": data_hash[:8],
    }

    # skip rendering if unchanged
    if data_hash != service.get_component_state(f"{component_id}_img_hash"):
        if client_id:
            # Render and send concurrently (async task)
            asyncio.create_task(
                render_and_send_fastplotlib(
                    fig, component_id, label, size, client_id, data_hash
                )
            )
        else:
            logger.warning(f"No client_id provided for {component_id}")

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


def matplotlib(fig: Optional[plt.Figure] = None, label: str = "plot") -> str:
    """Render a Matplotlib figure as a component."""
    service = PreswaldService.get_instance()

    if fig is None:
        fig, ax = plt.subplots()
        ax.plot([0, 1, 2], [0, 1, 4])

    # Save the figure as a base64-encoded PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode()

    # Generate a unique component ID based on the label
    component_id = f"matplotlib-{hashlib.md5(label.encode()).hexdigest()[:8]}"

    component = {
        "type": "matplotlib",
        "id": component_id,
        "label": label,
        "image": img_b64,  # Store the image data
    }

    service.append_component(component)

    return component_id  # Returning ID for potential tracking


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


def text(
    data: Union[str, int, float, bool, List[Union[str, int, float, bool]]],
    size: float = 1.0,
) -> str:
    """
    Create text/markdown component that supports strings,
    numbers, bools, and lists of strings or numbers.

    Args:
        data: String/Number/Bool or List of either
        size: Text size

    Returns:
        Formatted string of inputted data

    Raises:
        Logs and handles any string casting errors internally

    Notes:
        - Can raise TypeError on unsupported types, but types
          like dataframes and dicts still 'work'.
    """
    service = PreswaldService.get_instance()
    id = generate_id("text")

    if isinstance(data, list):
        processed_list = []
        for item in data:
            processed_list.append(str(item))
        combined_data = " ".join(processed_list)
    elif isinstance(data, (str, int, float, bool)):
        combined_data = str(data)
    else:
        logger.warning(f"Passing unsupported type: {type(data)} to text().")
        try:
            combined_data = str(data)
        except Exception as e:
            logger.error(f"Error: {e}")
            combined_data = ""

    logger.debug(f"Creating text component with id {id}")
    component = {
        "type": "text",
        "id": id,
        "markdown": combined_data,
        "value": combined_data,
        "size": size,
    }
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return data


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


def topbar() -> Dict:
    """Creates a topbar component."""
    service = PreswaldService.get_instance()
    id = generate_id("topbar")
    logger.debug(f"Creating topbar component with id {id}")
    component = {"type": "topbar", "id": id}
    logger.debug(f"Created component: {component}")
    service.append_component(component)
    return component


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


async def render_and_send_fastplotlib(
    fig: fplt.Figure,
    component_id: str,
    label: str,
    size: float,
    client_id: str,
    data_hash: str,
) -> Optional[str]:
    """
    Asynchronously renders a Fastplotlib figure to an offscreen canvas, encodes it as a PNG,
    and streams the resulting image data via WebSocket to the connected frontend client.

    This helper function handles rendering logic, alpha-blending, and ensures robust error
    handling. It updates the component state after successfully sending the image data.

    Args:
        fig (fplt.Figure): The fully configured Fastplotlib figure instance to render.
        component_id (str): Unique identifier for the component instance receiving this image.
        label (str): Human-readable label describing the component (for logging/debugging).
        size (float): Relative size of the component in the UI layout (0.0-1.0).
        client_id (str): WebSocket client identifier to route the rendered image correctly.
        data_hash (str): SHA-256 hash representing the figure state, used for cache invalidation.

    Returns:
        str: Returns "Render failed" if framebuffer blending fails, otherwise None.

    Raises:
        Logs and handles any exceptions internally without raising further.
    """
    service = PreswaldService.get_instance()

    fig.show()  # must call even in offscreen mode to initialize GPU resources

    # manually render the scene for all subplots
    for subplot in fig:
        subplot.viewport.render(subplot.scene, subplot.camera)

    # read from the framebuffer
    try:
        fig.canvas.request_draw()
        raw_img = np.asarray(fig.renderer.target.draw())

        if raw_img.ndim != 3 or raw_img.shape[2] != 4:
            raise ValueError(f"Unexpected image shape: {raw_img.shape}")

        # handle alpha blending
        alpha = raw_img[..., 3:4] / 255.0
        rgb = (raw_img[..., :3] * alpha + (1 - alpha) * 255).astype(np.uint8)

    except Exception as e:
        logger.error(f"Framebuffer blending failed for {component_id}: {e}")
        return "Render failed"

    # encode image to PNG
    img_buf = io.BytesIO()
    Image.fromarray(rgb).save(img_buf, format="PNG")
    png_bytes = img_buf.getvalue()

    # handle websocket communication
    client_websocket = service.websocket_connections.get(client_id)
    if client_websocket:
        packed_msg = msgpack.packb(
            {
                "type": "image_update",
                "component_id": component_id,
                "format": "png",
                "label": label,
                "size": size,
                "data": png_bytes,
            },
            use_bin_type=True,
        )

        try:
            await client_websocket.send_bytes(packed_msg)
            await service.handle_client_message(
                client_id,
                {
                    "type": "component_update",
                    "states": {f"{component_id}_img_hash": data_hash},
                },
            )
            logger.debug(f"✅ Sent {component_id} image to client {client_id}")
        except Exception as e:
            logger.error(f"WebSocket send failed for {component_id}: {e}")
    else:
        logger.warning(f"No active WebSocket found for client ID: {client_id}")
