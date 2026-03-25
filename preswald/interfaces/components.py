# Standard Library
import base64
import io
import json
import logging
import os
# Third-Party
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Internal
from preswald.engine.service import PreswaldService
from preswald.engine.render_tracking import with_render_tracking
from preswald.interfaces.component_return import ComponentReturn



# Configure logging
logger = logging.getLogger(__name__)

# NOTE to Developers: Please keep the components organized alphabetically

# Components

@with_render_tracking("alert")
def alert(message: str, level: str = "info", size: float = 1.0, component_id: str | None = None, **kwargs) -> ComponentReturn:
    """Create an alert component."""

    logger.debug(f"Creating alert component with id {component_id}, message: {message}")

    component = {
        "type": "alert",
        "id": component_id,
        "message": message,
        "level": level,
        "size": size,
    }

    return ComponentReturn(message, component)


@with_render_tracking("big_number")
def big_number(
    value: int | float | str,
    label: str | None = None,
    delta: str | None = None,
    delta_color: str | None = None,
    icon: str | None = None,
    description: str | None = None,
    size: float = 1.0,
    component_id: str | None = None,
    **kwargs,
) -> ComponentReturn:
    """Create a big number metric card component."""

    logger.debug(
        f"Creating big number component with id {component_id}, value: {value}"
    )

    component = {
        "type": "big_number",
        "id": component_id,
        "value": value,
        "label": label,
        "delta": delta,
        "delta_color": delta_color,
        "icon": icon,
        "description": description,
        "size": size,
    }

    logger.debug(f"Created component: {component}")

    return ComponentReturn(str(value), component)


@with_render_tracking("button")
def button(
    label: str,
    variant: str = "default",
    disabled: bool = False,
    loading: bool = False,
    size: float = 1.0,
    component_id: str | None = None,
    **kwargs
) -> ComponentReturn:
    """Create a button component that returns True when clicked."""
    service = PreswaldService.get_instance()

    # Get current state or use default
    current_value = service.get_component_state(component_id)
    if current_value is None:
        current_value = False

    component = {
        "type": "button",
        "id": component_id,
        "label": label,
        "variant": variant,
        "disabled": disabled,
        "loading": loading,
        "size": size,
        "value": current_value,
        "onClick": True,  # Always enable click handling
    }

    return ComponentReturn(current_value, component)

@with_render_tracking("checkbox")
def checkbox(label: str, default: bool = False, size: float = 1.0, component_id: str | None = None, **kwargs) -> ComponentReturn:
    """Create a checkbox component with consistent ID based on label."""
    service = PreswaldService.get_instance()

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

    return ComponentReturn(current_value, component)


@with_render_tracking("generic")
def generic(content: object, mimetype: str, component_id: str | None = None, **kwargs) -> ComponentReturn:
    """
    A generic rendering fallback that upgrades known mimetypes into rich components.

    If the mimetype is recognized, this function dynamically calls the mapped Preswald component.
    Otherwise, it returns a minimal generic component that just displays the raw value.
    """
    from preswald.interfaces.render.registry import get_component_type_for_mimetype
    from preswald import interfaces

    logger.debug(f"[generic] Rendering {mimetype=} with id={component_id}")

    component_type = get_component_type_for_mimetype(mimetype)

    if component_type and component_type != 'generic':
        component_fn = getattr(interfaces.components, component_type, None)
        if callable(component_fn):
            return component_fn(content, component_id=component_id, mimetype=mimetype, **kwargs)
        else:
            logger.warning(f"[generic] No such component function: {component_type=} for {mimetype=}")

    # Fallback to generic if no match or unsupported
    fallback_component = {
        "type": "generic",
        "id": component_id,
        "mimetype": mimetype,
        "value": content,
        **kwargs,
    }

    return ComponentReturn(content, fallback_component)


@with_render_tracking("image")
def image(src: str, alt: str = "Image", size: float = 1.0, component_id: str | None = None, **kwargs) -> ComponentReturn:
    """Create an image component.

    Args:
        src: The image source. Can be:
            - A URL to a remote image
            - A local file path (relative to the project root)
            - A base64 encoded image string
            - A data URI
        alt: Alternative text for the image
        size: Size of the component (0.0-1.0)
    """

    logger.debug(f"Creating image component with id {component_id}, src: {src}")

    # Handle different types of image sources
    processed_src = src

    # If it's a local file path, convert it to a data URL
    if isinstance(src, str) and not src.startswith(
        ("http://", "https://", "data:", "/")
    ):
        # Check if file exists in project's images directory
        project_images_dir = os.path.join(os.getcwd(), "images")
        local_path = os.path.join(project_images_dir, src)
        if os.path.exists(local_path):
            try:
                # Read the image file and convert to base64
                with open(local_path, "rb") as img_file:
                    img_data = img_file.read()
                    img_base64 = base64.b64encode(img_data).decode("utf-8")

                    # Get the file extension to determine MIME type
                    _, ext = os.path.splitext(src)
                    mime_type = {
                        ".png": "image/png",
                        ".jpg": "image/jpeg",
                        ".jpeg": "image/jpeg",
                        ".gif": "image/gif",
                        ".svg": "image/svg+xml",
                    }.get(ext.lower(), "image/png")

                    # Create data URL
                    processed_src = f"data:{mime_type};base64,{img_base64}"
            except Exception as e:
                logger.error(f"Error converting local image to data URL: {e}")
                processed_src = f"/images/{src}"  # Fallback to regular URL
        else:
            logger.warning(f"Local image file not found in images directory: {src}")

    component = {
        "type": "image",
        "id": component_id,
        "src": processed_src,
        "alt": alt,
        "size": size,
    }

    return ComponentReturn(component, component)


@with_render_tracking("json_viewer")
def json_viewer(
    data, title: str | None = None,
    expanded: bool = True,
    size: float = 1.0,
    component_id: str | None = None,
    **kwargs
) -> ComponentReturn:
    """Create a JSON viewer component with collapsible tree view."""
    # Attempt to ensure JSON is serializable and safe
    try:
        if isinstance(data, str):
            parsed_data = json.loads(data)
        else:
            parsed_data = data
        serializable_data = convert_to_serializable(parsed_data)
    except Exception as e:
        serializable_data = {"error": f"Invalid JSON: {e!s}"}

    component = {
        "type": "json_viewer",
        "id": component_id,
        "data": serializable_data,
        "title": title,
        "expanded": expanded,
        "size": size,
    }

    logger.debug(f"Created JSON viewer component with id {component_id}")
    return ComponentReturn(component, component)

@with_render_tracking("matplotlib")
def matplotlib(fig: plt.Figure | None = None, label: str = "plot", component_id: str | None = None, **kwargs) -> ComponentReturn:
    """Render a Matplotlib figure as a component."""

    if fig is None:
        fig, ax = plt.subplots()
        ax.plot([0, 1, 2], [0, 1, 4])

    # Save the figure as a base64-encoded PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode()

    component = {
        "type": "matplotlib",
        "id": component_id,
        "label": label,
        "image": img_b64,  # Store the image data
    }

    return ComponentReturn(
        component_id, component
    )  # Returning ID for potential tracking


@with_render_tracking("plotly")
def plotly(fig, size: float = 1.0, component_id: str | None = None, **kwargs) -> ComponentReturn:  # noqa: C901
    """
    Render a Plotly figure.

    Args:
        fig: A Plotly figure object.
    """

    try:
        import time

        start_time = time.time()
        logger.debug("[PLOTLY] Starting plotly render")
        logger.debug(f"[PLOTLY] Created plot component with id {component_id}")

        # Optimize the figure for web rendering
        optimize_start = time.time()

        # Reduce precision of numeric values
        for trace in fig.data:
            for attr in ["x", "y", "z", "lat", "lon"]:
                if hasattr(trace, attr):
                    values = getattr(trace, attr)
                    if isinstance(values, list | np.ndarray):
                        if np.issubdtype(np.array(values).dtype, np.floating):
                            setattr(trace, attr, np.round(values, decimals=4))

            # Optimize marker sizes
            if hasattr(trace, "marker") and hasattr(trace.marker, "size"):
                if isinstance(trace.marker.size, list | np.ndarray):
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
                if isinstance(value, list | np.ndarray):
                    trace[key] = [
                        (
                            None
                            if isinstance(x, float | np.floating) and np.isnan(x)
                            else x
                        )
                        for x in value
                    ]
                elif isinstance(value, float | np.floating) and np.isnan(value):
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
            "id": component_id,
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

        logger.debug(f"[PLOTLY] Plot data created successfully for id {component_id}")
        logger.debug(
            f"[PLOTLY] Total plotly render took {time.time() - start_time:.3f}s"
        )

        return ComponentReturn(component, component)

    except Exception as e:
        logger.error(f"[PLOTLY] Error creating plot: {e!s}", exc_info=True)
        error_component = {
            "type": "plot",
            "id": component_id,
            "error": f"Failed to create plot: {e!s}",
        }

        return ComponentReturn(error_component, error_component)

@with_render_tracking("progress")
def progress(label: str, value: float = 0.0, size: float = 1.0, component_id: str | None = None, **kwargs) -> ComponentReturn:
    """Create a progress component."""

    logger.debug(f"Creating progress component with id {component_id}, label: {label}")
    component = {
        "type": "progress",
        "id": component_id,
        "label": label,
        "value": value,
        "size": size,
    }

    return ComponentReturn(value, component)


@with_render_tracking("selectbox")
def selectbox(
    label: str,
    options: list[str],
    default: str | None = None,
    size: float = 1.0,
    component_id: str | None = None,
    **kwargs
) -> ComponentReturn:
    """Create a select component with consistent ID based on label."""
    service = PreswaldService.get_instance()
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

    logger.debug(f"[selectbox] ID={component_id}, selected={current_value}")

    return ComponentReturn(current_value, component)


@with_render_tracking("separator")
def separator(component_id: str | None = None, **kwargs) -> ComponentReturn:
    """Create a separator component that forces a new row."""
    component = {"type": "separator", "id": component_id}

    logger.debug(f"[separator] ID={component_id}")
    return ComponentReturn(component, component)


@with_render_tracking("slider")
def slider(
    label: str,
    min_val: float = 0.0,
    max_val: float = 100.0,
    step: float = 1.0,
    default: float | None = None,
    size: float = 1.0,
    component_id: str | None = None,
    **kwargs,
) -> ComponentReturn:
    """Create a slider component with consistent ID based on label"""
    service = PreswaldService.get_instance()

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

    logger.debug(f"[slider] ID={component_id}, value={current_value}")
    return ComponentReturn(current_value, component)


@with_render_tracking("spinner")
def spinner(
    label: str = "Loading...",
    variant: str = "default",
    show_label: bool = True,
    size: float = 1.0,
    component_id: str | None = None,
    **kwargs,
) -> ComponentReturn:
    """Create a loading spinner component.

    Args:
        label: Text to show below the spinner
        variant: Visual style ("default" or "card")
        show_label: Whether to show the label text
        size: Component width (1.0 = full width)
    """

    component = {
        "type": "spinner",
        "id": component_id,
        "label": label,
        "variant": variant,
        "showLabel": show_label,
        "size": size,
    }

    logger.debug(f"[spinner] ID={component_id}")
    return ComponentReturn(None, component)


@with_render_tracking("sidebar")
def sidebar(
    defaultopen: bool = False,
    component_id: str | None = None,
    logo: str | None = None,
    name: str | None = None,
    **kwargs
) -> ComponentReturn:
    """Create a sidebar component with optional logo and name."""
    component = {
        "type": "sidebar",
        "id": component_id,
        "defaultopen": defaultopen,
        "branding": {"logo": logo, "name": name},
    }

    logger.debug(
        f"[sidebar] ID={component_id}, defaultopen={defaultopen}, logo={logo}, name={name}"
    )
    return ComponentReturn(component, component)


@with_render_tracking("table")
def table(
    data: pd.DataFrame,
    title: str | None = None,
    limit: int | None = None,
    component_id: str | None = None,
    **kwargs
) -> ComponentReturn:
    """Create a table component that renders data using TableViewerWidget.

    Args:
        data: Pandas DataFrame or list of dictionaries to display.
        title: Optional title for the table.
        limit: Optional limit for rows displayed.

    Returns:
        ComponentReturn: Component metadata and processed data.
    """

    try:
        # Convert pandas DataFrame to a list of dictionaries if needed
        if hasattr(data, "to_dict"):
            if isinstance(data, pd.DataFrame):
                data = data.reset_index(drop=True)
                if limit is not None:
                    data = data.head(limit)
            data = data.to_dict("records")

        # Ensure data is a list
        if not isinstance(data, list):
            data = [data] if data else []

        # Ensure data is not empty before accessing keys
        if data and isinstance(data[0], dict):
            column_defs = [
                {"headerName": str(col), "field": str(col)} for col in data[0].keys()
            ]
        else:
            column_defs = []

        # Process each row to ensure JSON serialization
        processed_data = []
        for row in data:
            processed_row = {
                str(key): (
                    value.item()
                    if isinstance(value, np.integer | np.floating)
                    else value
                )
                if value is not None
                else ""  # Ensure no None values
                for key, value in row.items()
            }
            processed_data.append(processed_row)

        # Log debug info
        logger.debug(f"Column Definitions: {column_defs}")
        logger.debug(
            f"Processed Data (first 5 rows): {processed_data[:5]}"
        )  # Limit logs

        # Create AG Grid compatible component structure
        component = {
            "type": "table",
            "id": component_id,
            "props": {
                "columnDefs": column_defs,
                "rowData": processed_data,
                "title": str(title) if title else None,
            },
        }

        logger.debug(f"[table] ID={component_id}")
        return ComponentReturn(component, component)

    except Exception as e:
        logger.error(f"Error creating table component: {e!s}")
        error_component = {
            "type": "table",
            "id": component_id,
            "props": {
                "columnDefs": [],
                "rowData": [],
                "title": f"Error: {e!s}",
            },
        }

        return ComponentReturn(error_component, error_component)


@with_render_tracking("text")
def text(markdown_str: str, size: float = 1.0, component_id: str | None = None, **kwargs) -> ComponentReturn:
    """Create a text/markdown component."""
    component = {
        "type": "text",
        "id": component_id,
        "markdown": markdown_str,
        "value": markdown_str,
        "size": size,
    }

    logger.info(f"[text] ID = {component_id}, content = {markdown_str}")
    return ComponentReturn(markdown_str, component)


@with_render_tracking("text_input")
def text_input(
    label: str,
    placeholder: str = "",
    default: str = "",
    size: float = 1.0,
    component_id: str | None = None,
    **kwargs,
) -> ComponentReturn:
    """Create a text input component.

    Args:
        label: Label text shown above the input
        placeholder: Placeholder text shown when input is empty
        default: Initial value for the input
        size: Component width (1.0 = full width)

    Returns:
        ComponentReturn: Current value of the input, along with component metadata for rendering.
    """
    service = PreswaldService.get_instance()

    # Get current state or use default
    current_value = service.get_component_state(component_id)
    if current_value is None:
        current_value = default

    component = {
        "type": "text_input",
        "id": component_id,
        "label": label,
        "placeholder": placeholder,
        "value": current_value,
        "size": size,
    }

    logger.debug(f"[text_input] ID={component_id}, value={current_value}")
    return ComponentReturn(current_value, component)


@with_render_tracking("topbar")
def topbar(component_id: str | None = None, **kwargs) -> ComponentReturn:
    """Creates a topbar component."""
    component = {"type": "topbar", "id": component_id}

    logger.debug(f"[topbar] ID={component_id}")
    return ComponentReturn(component, component)


# Helpers


def convert_to_serializable(obj: object) -> object:
    """Convert numpy arrays and other non-serializable objects to Python native types."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.int8 | np.int16 | np.int32 | np.int64 | np.integer):
        return int(obj)
    elif isinstance(obj, np.float16 | np.float32 | np.float64 | np.floating):
        if np.isnan(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list | tuple):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, np.generic):
        if np.isnan(obj):
            return None
        return obj.item()
    return obj
